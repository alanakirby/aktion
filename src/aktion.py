#!/usr/bin/env python

import boto3
from botocore.exceptions import ClientError
import os
import subprocess
import requests
import json
import difflib
import filecmp
import pyfiglet
import re

def lambda_handler(event, context):
    #  Banner
    print('___________________________________________________________________\n\n')
    ascii_banner = pyfiglet.figlet_format('              AKTION')
    print(ascii_banner)
    print('                   Created by Alana Kirby.')
    print('___________________________________________________________________')
    print('This script finds out what the latest AWS Services and Actions are\nand sends an email with them inside it.\n')
    print('Purpose: Keep up to date with policy management.')
    print('___________________________________________________________________')

    # Set variables
    print('Connecting to bucket.......................................( ͡° ͜ʖ ͡°)')
    s3_resource = boto3.resource('s3')
    s3_client = boto3.client('s3')
    bucket = os.environ.get('BUCKET_NAME')
    key = '/tmp/output.txt'

    # Download last file
    print('Loading yesterday\'s services................................(~˘▾˘)~')
    s3_client.download_file(bucket, key, '/tmp/past-output.txt')

    print('Gathering today\'s services..................................~(˘▾˘~)')
    response = requests.get('https://awspolicygen.s3.amazonaws.com/js/policies.js')
    content_json = response.content.decode('UTF-8').lstrip('app.PolicyEditorConfig=')
    content_dict = json.loads(content_json)['serviceMap']

    service_actions = []
    for service_name, values in content_dict.items():
        for action in values['Actions']:
            service_actions.append(f'{service_name}:{action}')

    service_actions.sort()

    service_string = '\n'.join(service_actions)

    with open('/tmp/output.txt', 'w') as f:
            f.write(service_string)

    # Store list in S3 and upload file
    print('Storing today\'s services in S3.......................ヽ(〃＾▽＾〃)ﾉ')
    s3_client.upload_file('/tmp/output.txt', bucket, '/tmp/output.txt')

    # Download new file - remove download and just use output.txt
    print('Loading today\'s services...............................(づ｡◕‿‿◕｡)づ')
    s3_client.download_file(bucket, key, '/tmp/latest-output.txt')

    # Compare files
    print('Comparing services...................(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ ✧ﾟ･: *ヽ(◕ヮ◕ヽ)')
    past_file = open('/tmp/past-output.txt').readlines()
    latest_file = open('/tmp/latest-output.txt').readlines()

    with open('/tmp/difference.txt', 'w') as d:
        for line in difflib.unified_diff(past_file, latest_file):
            d.write(line)

    # array
    array = []

    # Delete dumb extra bits
    with open('/tmp/difference.txt', 'r') as file:
        for line in file.readlines():
            if re.match(r"^\+\w", line):
                remove = re.sub(r"^\++", '', line)
                if remove.strip() is not '':
                    array.append(remove)

    with open('/tmp/difference.txt', 'w') as c:
        result = ''.join(array)
        c.write(result)

    diff_new = open('/tmp/difference.txt', 'r')
    diff_read = diff_new.read()


    SENDER = os.environ.get('SENDER_EMAIL')
    RECIPIENT = os.environ.get('RECEIVER_EMAIL')
    SES_REGION = os.environ.get('SES_REGION')

    # if its empty don't send it
    if os.path.getsize('/tmp/difference.txt') > 0:
    # n = print(new_services)
        print('___________________________________________________________________')
        print('Any new services and actions will appear in the difference.txt file\nand will be sent to an email weekly.')
        print('___________________________________________________________________')

        # AWS SES
        SUBJECT = 'New AWS Services and Actions have been released this week!'
        BODY_TEXT = ('New AWS Services and Actions have been released this week!\n'
                     'Here are the newbies to action on:\n' + str(diff_read))
        BODY_HTML = """<html>
                            <head></head>
                            <body>
                                <h1>New AWS Services and Actions have been released this week!</h1>
                                <p>Here are the newbies to action on:\n</p>
                            """ + str(diff_read) + """
                            </body>
                       </html>"""

        CHARSET = 'UTF-8'

        ses_client = boto3.client('ses',region_name=SES_REGION)

        try:
            ses_response = ses_client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,
            )

        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(ses_response['MessageId'])
    else:
        print('___________________________________________________________________')
        print('Any new services and actions will appear in the difference.txt file\nand will be sent to your email weekly.')
        print('___________________________________________________________________')

        # AWS SES
        SUBJECT = 'AWS has taken a holiday this week!'
        BODY_TEXT = ('AWS has taken a holiday this week!\n'
                     'No new services or actions this week.')
        BODY_HTML = """<html>
                            <head></head>
                            <body>
                                <h1>AWS has taken a holiday this week!</h1>
                                <p>No new services or actions this week.</p>
                            </body>
                       </html>"""

        CHARSET = 'UTF-8'

        ses_client = boto3.client('ses',region_name=SES_REGION)

        try:
            ses_response = ses_client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                    'BccAddresses': [
                        BCC,
                    ],
                },
                Message={
                    'Body': {
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,
            )

        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(ses_response['MessageId'])
