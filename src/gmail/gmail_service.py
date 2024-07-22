from googleapiclient.discovery import build
from src.data.models import Email
from datetime import datetime, timezone
import email.utils
import base64

class GmailService:
    def __init__(self, gmail_service):
        self.service = gmail_service

    def fetch_emails(self, max_results=100):
        results = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])

        emails = []
        for message in messages:
            # print(message)
            email = self.get_email_details(message['id'])
            emails.append(email)

        return emails

    def get_email_details(self, message_id):
        message = self.service.users().messages().get(userId='me', id=message_id).execute()
        
        headers = {header['name'].lower(): header['value'] for header in message['payload']['headers']}
        
        subject = headers.get('subject', '')
        sender = headers.get('from', '')
        recipient = headers.get('to', '')
        date_str = headers.get('date', '')

        body = self.get_email_body(message)

        # Parse the date using email.utils and ensure it's UTC
        parsed_date = email.utils.parsedate_to_datetime(date_str)
        utc_date = parsed_date.astimezone(timezone.utc)

        return Email.create(
            message_id=message_id,
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            received_date=utc_date
        )

    def get_email_body(self, message):
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    return self.decode_body(part['body'].get('data', ''))
        elif 'body' in message['payload']:
            return self.decode_body(message['payload']['body'].get('data', ''))
        return ""

    def decode_body(self, encoded_body):
        """Decode base64url encoded body."""
        if not encoded_body:
            return ""
        decoded_bytes = base64.urlsafe_b64decode(encoded_body)
        return decoded_bytes.decode('utf-8')

    def mark_as_read(self, message_id):
        self.service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()

    def mark_as_unread(self, message_id):
        self.service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': ['UNREAD']}).execute()

    def move_message(self, message_id, label_id):
        label_id = label_id.upper()
        if label_id in ['INBOX', 'SPAM', 'TRASH']:
            # Remove all other system labels and add the new one
            remove_labels = set(['INBOX', 'SPAM', 'TRASH']) - set([label_id])
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={
                    'removeLabelIds': list(remove_labels),
                    'addLabelIds': [label_id]
                }
            ).execute()
        else:
            raise ValueError(f"Unsupported label: {label_id}. Only INBOX, SPAM, and TRASH are supported.")
