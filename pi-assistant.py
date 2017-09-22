#!/usr/bin/env python3
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os.path
import json
from time import sleep

import RPi.GPIO as GPIO

import google.oauth2.credentials
from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file

PIN_BTN = 17
PIN_LED = 22
ASSISTANT = None

def callback(channel):
    global CREDENTIALS
    if not CREDENTIALS:
        return
    print("callback")
    assistant = Assistant(CREDENTIALS)
    ret = assistant.start_conversation()
    print(ret)

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_BTN, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(PIN_LED, GPIO.OUT)
GPIO.output(PIN_LED, GPIO.LOW)

def callback_start_conversation(channel):
    global ASSISTANT
    if not ASSISTANT:
        return
    ASSISTANT.start_conversation()

def process_event(event):
    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        print('Google Assistant is listening to you now.')
        GPIO.output(PIN_LED, GPIO.HIGH)
    if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
        print("You:", event.args['text'])
    if event.type == EventType.ON_ALERT_STARTED:
        print('An alert has started sounding.')
    if event.type == EventType.ON_ALERT_FINISHED:
        print('The alert has finished sounding.')
    if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
            event.args and event.args['with_follow_on_turn'] == True):
        #print('Google Assistant is listening to your response.')
        pass
    if event.type == EventType.ON_END_OF_UTTERANCE:
        print('Google Assistant may not have understood what you has said')
    if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
            event.args and event.args['with_follow_on_turn'] == False):
        print('Conversation finished.')
        GPIO.output(PIN_LED, GPIO.LOW)

def main():
    global ASSISTANT

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='Path to store and read OAuth2 credentials')
    args = parser.parse_args()
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))
    ASSISTANT = Assistant(credentials)
    GPIO.add_event_detect(PIN_BTN, GPIO.FALLING,
                callback=callback_start_conversation, bouncetime=300)
    for event in ASSISTANT.start():
        process_event(event)

    while True:
        pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Google Assistant finised.")
        GPIO.cleanup()