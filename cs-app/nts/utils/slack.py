import os
import logging

import requests

log = logging.getLogger(__name__)

def post_message(message):
    log.info('Posting message to slack')
    slack_web_hook = os.getenv('SLACK_WEB_HOOK')
    try:
        resp = requests.post(
            url=slack_web_hook,
            headers={'Content-type': 'application/json'},
            data={'text': message}
        )
        resp.raise_for_status()
    except Exception as error:
        log.error('An error occured posting to slack- %s', error)