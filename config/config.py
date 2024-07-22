import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self._config = {
            'SCOPES': ['https://www.googleapis.com/auth/gmail.modify'],
            'DATABASE_URI': os.environ.get('DATABASE_URI', 'sqlite:///emails.db'),
            'RULES_FILE': os.environ.get('RULES_FILE', 'config/rules.json'),
            'MAX_EMAILS': int(os.environ.get('MAX_EMAILS', 10)),
            'GMAIL_CLIENT_ID': os.getenv('GMAIL_CLIENT_ID'),
            'GMAIL_CLIENT_SECRET': os.getenv('GMAIL_CLIENT_SECRET'),
            'GMAIL_PROJECT_ID': os.getenv('GMAIL_PROJECT_ID'),
        }

    def __getitem__(self, key):
        return self._config[key]

    def get(self, key, default=None):
        return self._config.get(key, default)

config = Config()