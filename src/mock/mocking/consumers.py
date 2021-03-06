import json
import logging
from channels import Group
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
from .models import *
from django.db import IntegrityError, transaction
from queue import *
import threading
from datetime import *
from django.utils import timezone
from django.db.models import Q

log = logging.getLogger(__name__)
interviewer_queue = PriorityQueue()
interviewee_queue = PriorityQueue()
# set to mark ids in two queues
interviewer_ids = {}
interviewee_ids = {}
connected_status = {}  # value: 0 for interviewer, 1 for interviewee
lock = threading.RLock()


# basic idea for matching: there are two queues, we put user to different queues according to their current role
# need to handle race condition and disconnection
# use lazy deletion to handle disconnection: determine if the item is valid when polling it out of the queue
# remember to update use status and also message mapping

# prefix interview for code synchronization, chat for chatting, match for interview matching
class QueueItem:
    def __init__(self, message, pid):
        self.uid = message.user.pk
        self.rating = message.user.profile.rating
        self.pid = pid  # problem id
        return

    def __lt__(self, other):
        selfPriority = (self.rating, self.uid)
        otherPriority = (other.rating, other.uid)
        return selfPriority > otherPriority


@channel_session_user_from_http
def ws_connect(message):
    try:
        parameters = message['path'].strip('/').split('/')
        prefix = parameters[0]
        label = parameters[1]
        if prefix == 'interview':
            interview = Interview.objects.get(pk=label)
            log.debug('interview %d', interview.pk)
            Group('interview_' + label, channel_layer=message.channel_layer).add(message.reply_channel)
            message.channel_session['interview'] = label
            last = timezone.now() - interview.created_at
            remain = 45 * 60 - last.total_seconds()
            if remain < 0:
                remain = 0
            data = {"type": "time", "time": remain}
            message.reply_channel.send({"text": json.dumps(data)})


        elif prefix == 'match':
            label = int(label)
            uid = message.user.pk
            if label == 0:
                problem_id = parameters[2]
                # check if problem_id is legal
                if len(Problem.objects.filter(pk=problem_id)) == 0:
                    return
            else:
                problem_id = -1  # no problem id for interviewee
            if not message.user.pk:
                log.debug('no valid user')
                return
            if label != 0 and label != 1:
                return
            if message.user.pk in connected_status:
                # a match seesion running
                return
            if label == 1 and message.user.profile.interview_credit <= 0:
                # no interview credit
                return
            now = timezone.now()
            start_time = now - timedelta(minutes=45)
            interviews = Interview.objects.filter(created_at__gt=start_time). \
                filter(Q(interviewee=message.user) | Q(interviewer=message.user)).order_by('-created_at')
            if len(interviews) > 0:
                # ongoing interview
                return
            message.channel_session['match'] = message.user.pk
            match(label, message, problem_id, uid)

        else:
            log.debug('invalid ws path=%s', message['path'])
            return
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Interview.DoesNotExist:
        log.debug('ws interview does not exist label=%s', label)
        return


@channel_session_user
@transaction.atomic
def ws_receive(message):
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['interview']
        room = Interview.objects.filter(pk=label).select_for_update()[0]
        now = datetime.now(timezone.utc)
        elapsedTime = now - room.created_at
        seconds = elapsedTime.total_seconds()
        log.debug('elapsed seconds:%d', seconds)
        if seconds > 45 * 60:
            # time out
            return

    except KeyError:
        log.debug('no room in channel_session')
        return
    except Interview.DoesNotExist:
        log.debug('recieved message, buy room does not exist label=%s', label)
        return

    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", message['text'])
        return

    if data:
        if 'type' not in data:
            log.debug("no type information")
            return
        if data['type'] == "code":
            if not message.user.pk == room.interviewee.pk:
                # only interviewee can edit the code
                return
            if set(data.keys()) != {'handle', 'type', 'start', 'end', 'change'}:
                log.debug("ws message unexpected format data=%s", data)
                return
            log.debug('chat message room=%s handle=%s start=%d end=%d change=%s',
                      room.pk, data['handle'], data['start'], data['end'], data['change'])

            # See above for the note about Group
            content = room.content
            room.content = content[:data['start'] + 1] + data['change'] + content[data['end']:]
            print(room.content)
            room.save()
            Group('interview_' + label, channel_layer=message.channel_layer).send({'text': json.dumps(data)})


        elif data['type'] == "chat":
            if set(data.keys()) != {'type', 'message'}:
                log.debug("ws message unexpected format data=%s", data)
                return
            log.debug('chat message room=%s message=%s',
                      room.pk, data['message'])

            data['handle'] = message.user.username
            chatmessage = ChatMessage(handle=data['handle'], interview=room, content=data['message'])
            chatmessage.save()
            data['created_at'] = chatmessage.formatted_timestamp
            # See above for the note about Group
            Group('interview_' + label, channel_layer=message.channel_layer).send({'text': json.dumps(data)})


        else:
            log.debug("message type error")


@channel_session_user
def ws_disconnect(message):
    if 'interview' in message.channel_session:
        try:
            label = message.channel_session['interview']
            room = Interview.objects.get(pk=label)
            Group('interview_' + label, channel_layer=message.channel_layer).discard(message.reply_channel)
        except (KeyError, Interview.DoesNotExist):
            pass
    elif 'match' in message.channel_session:
        lock.acquire()
        del connected_status[message.channel_session['match']]
        lock.release()


# match two users
def match(label, message, problem_id, uid):
    try:
        lock.acquire()
        connected_status[message.user.pk] = label
        item = None
        if label == 0:
            # interviewer
            while item is None:
                item = interviewee_queue.get_nowait()
                message2 = interviewee_ids[item.uid]
                del interviewee_ids[item.uid]
                if item.uid not in connected_status or connected_status[item.uid] != 1:
                    # wrong status
                    item = None
            interview = Interview(interviewee_id=item.uid, interviewer_id=message.user.pk,
                                  problem_id=problem_id)
        else:
            while item is None:
                item = interviewer_queue.get_nowait()
                message2 = interviewer_ids[item.uid]
                del interviewer_ids[item.uid]
                if item.uid not in connected_status or connected_status[item.uid] != 0:
                    # wrong status
                    item = None
            interview = Interview(interviewer_id=item.uid, interviewee_id=message.user.pk, problem_id=item.pid)
        # matching succeed
        interview.save()
        message.reply_channel.send({"text": str(interview.pk)})
        message2.reply_channel.send({"text": str(interview.pk)})
        # modify credits
        interviewer = Profile.objects.get(user_id=interview.interviewer_id)
        interviewer.interview_credit += 1
        interviewer.save()
        interviewee = Profile.objects.get(user_id=interview.interviewee_id)
        interviewee.interview_credit -= 1
        interviewee.save()
    except Empty:
        # interviewee_queue is empty
        if label == 0:
            if uid not in interviewer_ids:
                interviewer_queue.put_nowait(QueueItem(message, problem_id))
            interviewer_ids[uid] = message
        else:
            if uid not in interviewee_ids:
                interviewee_queue.put_nowait(QueueItem(message, problem_id))
            interviewee_ids[uid] = message
    finally:
        lock.release()