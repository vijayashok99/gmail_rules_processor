import logging
from contextlib import contextmanager
from src.auth.gmail_authenticator import GmailAuthenticator, GmailServiceFactory
from src.data.models import Base
from src.data.repository import EmailRepository
from src.gmail.gmail_service import GmailService
from src.rules.rule_processor import RuleProcessor, RuleMatcher
from config.config import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    engine = create_engine(
        config['DATABASE_URI'],
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    try:
        logger.info("Authenticating...")
        authenticator = GmailAuthenticator(config)
        gmail_api_service = GmailServiceFactory.create_service(authenticator)
        gmail_service = GmailService(gmail_api_service)

        rule_processor = RuleProcessor.from_file(config['RULES_FILE'], gmail_service)

        logger.info("Fetching Emails...")
        emails = gmail_service.fetch_emails(max_results=config['MAX_EMAILS'])

        logger.info(f"Fetched {len(emails)} Emails")

        logger.info("Initiating Rules Processor...")
        with session_scope(Session) as session:
            email_repo = EmailRepository(session)
            for email in emails:
                logger.info(f"Processing Email Subject: {email.subject}")
                existing_email = email_repo.get_email_by_message_id(email.message_id)
                if not existing_email:
                    email_repo.add_email(email)
                rule_processor.process_email(email)
        
        logger.info("Rules Applied Successfully!")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        logger.info("All resources released. Terminated Successfully")

@contextmanager
def session_scope(Session):
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
