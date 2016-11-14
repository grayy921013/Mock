import json
import logging
from channels import Group
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
from .models import Interview
from django.db import IntegrityError, transaction
from queue import *

log = logging.getLogger(__name__)
interviewer_queue = PriorityQueue()
interviewee_queue = PriorityQueue()

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
        prefix, label = message['path'].strip('/').split('/')
        if prefix == 'interview':
            interview = Interview.objects.get(pk=label)
            log.debug('interview %d', interview.pk)
            Group('interview_' + label, channel_layer=message.channel_layer).add(message.reply_channel)
            message.channel_session['interview'] = label
        elif prefix == 'match':
            if not message.user.pk:
                log.debug('no valid user')
                return
            label = int(label)
            if label != 0 and label != 1:
                return
            message.channel_session['match'] = label
            try:
                if label == 0:
                    # interviewer
                    item = interviewee_queue.get_nowait()
                    interview = Interview(interviewee_id=item.uid, interviewer_id=message.user.pk, problem_id=1)
                else:
                    item = interviewer_queue.get_nowait()
                    interview = Interview(interviewer_id=item.uid, interviewee_id=message.user.pk, problem_id=1)
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
        if not message.user.pk == room.interviewer.pk:
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

@channel_session_user
def ws_disconnect(message):
    if 'interview' in message.channel_session:
        try:
            label = message.channel_session['interview']
            room = Interview.objects.get(pk=label)
            Group('interview_'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
        except (KeyError, Interview.DoesNotExist):
            pass
