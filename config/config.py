import os
from dotenv import load_dotenv

load_dotenv()

# As its a test project, pasting all this values in directly. In prod we won't use this way
class Config:
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify'] # TODO: Think its enough Scope for our usecase. Anyways have a look
    
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sql/test')
    
    RULES_FILE = os.environ.get('RULES_FILE', 'config/rules.json')
    
    MAX_EMAILS = int(os.environ.get('MAX_EMAILS', 10))

    # Gmail API credentials
    GMAIL_CLIENT_ID = os.getenv('GMAIL_CLIENT_ID')
    GMAIL_CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET')
    GMAIL_PROJECT_ID = os.getenv('GMAIL_PROJECT_ID')
