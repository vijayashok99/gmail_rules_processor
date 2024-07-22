from sqlalchemy.orm import Session
from typing import List, Optional
from .models import Email

class EmailRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_email(self, email: Email) -> None:
        self.session.add(email)
        self.session.commit()

    def get_email_by_message_id(self, message_id: str) -> Optional[Email]:
        return self.session.query(Email).filter(Email.message_id == message_id).first()

    def update_email(self, email: Email) -> None:
        self.session.merge(email)
        self.session.commit()

    def get_all_emails(self) -> List[Email]:
        return self.session.query(Email).all()

    def delete_email(self, email: Email) -> None:
        self.session.delete(email)
        self.session.commit()