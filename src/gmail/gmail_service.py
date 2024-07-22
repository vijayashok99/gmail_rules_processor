from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.data.models import Email
from datetime import datetime, timezone
import email.utils
import base64
from typing import List, Optional

class GmailService:
    MIME_TYPE_PLAIN = 'text/plain'
    USER_ID = 'me'

    def __init__(self, gmail_service: build):
        self.service = gmail_service

    def fetch_emails(self, max_results: int = 100) -> List[Email]:
        try:
            results = self.service.users().messages().list(userId=self.USER_ID, maxResults=max_results).execute()
            messages = results.get('messages', [])
            return [self.get_email_details(message['id']) for message in messages]
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def get_email_details(self, message_id: str) -> Optional[Email]:
        try:
            message = self.service.users().messages().get(userId=self.USER_ID, id=message_id).execute()
            headers = {header['name'].lower(): header['value'] for header in message['payload']['headers']}
            
            subject = headers.get('subject', '')
            sender = headers.get('from', '')
            recipient = headers.get('to', '')
            date_str = headers.get('date', '')

            body = self.get_email_body(message)
            received_date = email.utils.parsedate_to_datetime(date_str)

            return Email.create(
                message_id=message_id,
                sender=sender,
                recipient=recipient,
                subject=subject,
                body=body,
                received_date=received_date
            )
        except HttpError as error:
            print(f'An error occurred while fetching email details: {error}')
            return None

    def get_email_body(self, message: dict) -> str:
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == self.MIME_TYPE_PLAIN:
                    return self.decode_body(part['body'].get('data', ''))
        elif 'body' in message['payload']:
            return self.decode_body(message['payload']['body'].get('data', ''))
        return ""

    @staticmethod
    def decode_body(encoded_body: str) -> str:
        if not encoded_body:
            return ""
        decoded_bytes = base64.urlsafe_b64decode(encoded_body)
        return decoded_bytes.decode('utf-8')

    def modify_message(self, message_id: str, add_labels: List[str] = None, remove_labels: List[str] = None) -> None:
        try:
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
            self.service.users().messages().modify(userId=self.USER_ID, id=message_id, body=body).execute()
        except HttpError as error:
            print(f'An error occurred while modifying the message: {error}')

    def mark_as_read(self, message_id: str) -> None:
        self.modify_message(message_id, remove_labels=['UNREAD'])

    def mark_as_unread(self, message_id: str) -> None:
        self.modify_message(message_id, add_labels=['UNREAD'])

    def move_message(self, message_id: str, label_id: str) -> None:
        label_id = label_id.upper()
        if label_id in ['INBOX', 'SPAM', 'TRASH']:
            remove_labels = set(['INBOX', 'SPAM', 'TRASH']) - {label_id}
            self.modify_message(message_id, add_labels=[label_id], remove_labels=list(remove_labels))
        else:
            raise ValueError(f"Unsupported label: {label_id}. Only INBOX, SPAM, and TRASH are supported.")
