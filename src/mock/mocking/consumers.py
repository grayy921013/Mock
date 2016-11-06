import json
import logging
from channels import Group
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
from .models import Interview
from django.db import IntegrityError, transaction

log = logging.getLogger(__name__)

@channel_session_user_from_http
def ws_connect(message):
    try:
        prefix, label = message['path'].strip('/').split('/')
        if prefix != 'interview':
            log.debug('invalid ws path=%s', message['path'])
            return
        room = Interview.objects.get(pk=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Interview.DoesNotExist:
        log.debug('ws interview does not exist label=%s', label)
        return

    #log.debug('interview connect room=%s client=%s:%s',
       # room.label, message['client'][0], message['client'][1])
    
    # Need to be explicit about the channel layer so that testability works
    # This may be a FIXME?
    Group('interview_'+label, channel_layer=message.channel_layer).add(message.reply_channel)

    message.channel_session['interview'] = label

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
        print( content[:data['start']+1])
        print(content[data['end']:])
        room.save()
        Group('interview_'+label, channel_layer=message.channel_layer).send({'text': json.dumps(data)})

@channel_session_user
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        room = Interview.objects.get(pk=label)
        Group('interview_'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, Interview.DoesNotExist):
        pass
