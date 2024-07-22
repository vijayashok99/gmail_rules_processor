import logging
from contextlib import contextmanager
from src.auth.gmail_authenticator import GmailAuthenticator
from src.data.models import Base
from src.data.repository import EmailRepository
from src.gmail.gmail_service import GmailService
from src.rules.rule_processor import RuleProcessor
from config.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    config = Config()

    # Set up database with connection pooling
    engine = create_engine(
        config.DATABASE_URI,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    try:
        # Authenticate and get Gmail service
        logging.info("Authenticating...")
        authenticator = GmailAuthenticator(config)
        gmail_api_service = authenticator.get_gmail_service()
        gmail_service = GmailService(gmail_api_service)

        # Set up rule processor
        rule_processor = RuleProcessor(config.RULES_FILE)

        # Fetch emails
        logging.info("Fetching Emails...")
        emails = gmail_service.fetch_emails(max_results=config.MAX_EMAILS)

        logging.info(f"Fetched {len(emails)} Emails")

        # Process emails
        logging.info("Initiating Rules Processor...")
        with session_scope(Session) as session:
            email_repo = EmailRepository(session)
            for email in emails:
                logging.info(f"Processing Email Subject: {email.subject}")
                existing_email = email_repo.get_email_by_message_id(email.message_id)
                if not existing_email:
                    email_repo.add_email(email)
                    rule_processor.process_email(email, gmail_service)
        
        logging.info("Rules Applied Successfully!")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        logging.info("All resources released. Terminated Successfully")

@contextmanager
def session_scope(Session):
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Database error: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()