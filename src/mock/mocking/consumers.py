import json
import logging
from channels import Group
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
from .models import Interview
from django.db import IntegrityError, transaction
from queue import *
import threading

log = logging.getLogger(__name__)
interviewer_queue = PriorityQueue()
interviewee_queue = PriorityQueue()
connected_status = {}  # value: 0 for interviewer, 1 for interviewee
lock = threading.RLock()

# prefix interview for code synchronization, chat for chatting, match for interview matching
class QueueItem:
    def __init__(self, message):
        self.message = message
        self.uid = message.user.pk
        self.rating = message.user.profile.rating
        return

    def __cmp__(self, other):
        # so that item with larger rating will come first
        if self.rating > other.rating:
            return -1
        elif self.rating == other.rating:
            return 0
        else:
            return 1

    def send(self, message):
        self.message.reply_channel.send(message)


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
        elif prefix == 'chat':
            interview = Interview.objects.get(pk=label)
            log.debug('interview %d', interview.pk)
            Group('chat_' + label, channel_layer=message.channel_layer).add(message.reply_channel)
            message.channel_session['chat'] = label
        elif prefix == 'match':
            problem_id = parameters[2]
            if not message.user.pk:
                log.debug('no valid user')
                return
            label = int(label)
            if label != 0 and label != 1:
                return
            if message.user.pk in connected_status:
                # a match seesion running
                return
            message.channel_session['match'] = message.user.pk
            try:
                lock.acquire()
                connected_status[message.user.pk] = label
                item = None
                if label == 0:
                    # interviewer
                    while item is None:
                        item = interviewee_queue.get_nowait()
                        if item.uid not in connected_status or connected_status[item.uid] != 1:
                            # wrong status
                            item = None
                    interview = Interview(interviewee_id=item.uid, interviewer_id=message.user.pk, problem_id=problem_id)
                else:
                    while item is None:
                        item = interviewer_queue.get_nowait()
                        if item.uid not in connected_status or connected_status[item.uid] != 0:
                            # wrong status
                            item = None
                    interview = Interview(interviewer_id=item.uid, interviewee_id=message.user.pk, problem_id=problem_id)
                # matching succeed
                interview.save()
                message.reply_channel.send({"text": str(interview.pk)})
                item.send({"text": str(interview.pk)})
            except Empty:
                # interviewee_queue is empty
                if label == 0:
                    interviewer_queue.put_nowait(QueueItem(message))
                else:
                    interviewee_queue.put_nowait(QueueItem(message))
            finally:
                lock.release()
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
    if 'interview' in message.channel_session:
        try:
            label = message.channel_session['interview']
            room = Interview.objects.filter(pk=label).select_for_update()[0]
            if not message.user.pk == room.interviewee.pk:
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

        if set(data.keys()) != {'handle', 'start', 'end', 'change'}:
            log.debug("ws message unexpected format data=%s", data)
            return

        if data:
            log.debug('chat message room=%s handle=%s start=%d end=%d change=%s',
                room.pk, data['handle'], data['start'], data['end'], data['change'])

            # See above for the note about Group
            content = room.content
            room.content = content[:data['start']+1] + data['change'] + content[data['end']:]
            print(room.content)
            room.save()
            Group('interview_'+label, channel_layer=message.channel_layer).send({'text': json.dumps(data)})
    else:
        try:
            label = message.channel_session['interview']
            room = Interview.objects.filter(pk=label)[0]
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

        if set(data.keys()) != {'handle', 'message'}:
            log.debug("ws message unexpected format data=%s", data)
            return

        if data:
            log.debug('chat message room=%s message=%s',
                          room.pk, data['handle'], data['message'])

            # See above for the note about Group
            Group('chat_' + label, channel_layer=message.channel_layer).send({'text': json.dumps(data)})
@channel_session_user
def ws_disconnect(message):
    if 'interview' in message.channel_session:
        try:
            label = message.channel_session['interview']
            room = Interview.objects.get(pk=label)
            Group('interview_'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
        except (KeyError, Interview.DoesNotExist):
            pass
    elif 'chat' in message.channel_session:
        try:
            label = message.channel_session['chat']
            room = Interview.objects.get(pk=label)
            Group('chat_'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
        except (KeyError, Interview.DoesNotExist):
            pass
    elif 'match' in message.channel_session:
        lock.acquire()
        del connected_status[message.channel_session['match']]
        lock.release()
