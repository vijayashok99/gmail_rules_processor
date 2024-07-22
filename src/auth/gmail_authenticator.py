import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailAuthenticator:
    def __init__(self, config):
        self.config = config
        self.creds = None

    def authenticate(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.config['SCOPES'])
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": self.config['GMAIL_CLIENT_ID'],
                            "client_secret": self.config['GMAIL_CLIENT_SECRET'],
                            "project_id": self.config['GMAIL_PROJECT_ID'],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "redirect_uris": ["http://localhost"]
                        }
                    },
                    scopes=self.config['SCOPES']
                )
                self.creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

class GmailServiceFactory:
    @staticmethod
    def create_service(authenticator):
        if not authenticator.creds:
            authenticator.authenticate()
        return build('gmail', 'v1', credentials=authenticator.creds)
