import sys
sys.path.insert(0, '.')
from scripts.gmail_client import GmailClient

client = GmailClient()
result = client.list_messages(query='from:erica', max_results=10)
messages = result.get('messages', [])
print(f'Found {len(messages)} messages from erica')
print()

for msg_ref in messages:
    msg = client.get_message(msg_ref['id'])
    headers = client.get_message_headers(msg)
    subject = headers.get('Subject', '(no subject)')
    sender = headers.get('From', '')
    date = headers.get('Date', '')
    body = client.get_message_body(msg)
    print(f'Subject: {subject}')
    print(f'From: {sender}')
    print(f'Date: {date}')
    print(f'Preview: {body[:500]}')
    print('---')
