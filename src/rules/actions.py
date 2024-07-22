from enum import Enum, auto
from src.data.models import Email
from typing import Any, Dict

class Action(Enum):
    MARK_AS_READ = auto()
    MARK_AS_UNREAD = auto()
    MOVE_TO_INBOX = auto()
    MOVE_TO_SPAM = auto()
    MOVE_TO_TRASH = auto()

def mark_as_read(email: Email, gmail_service: Any, parameters: Dict[str, Any]) -> None:
    gmail_service.mark_as_read(email.message_id)

def mark_as_unread(email: Email, gmail_service: Any, parameters: Dict[str, Any]) -> None:
    gmail_service.mark_as_unread(email.message_id)

def move_message(email: Email, gmail_service: Any, parameters: Dict[str, Any]) -> None:
    label_id = parameters.get('label_id')
    if not label_id:
        raise ValueError("Label ID is required for move_message action")
    gmail_service.move_message(email.message_id, label_id)

ACTION_FUNCTIONS = {
    Action.MARK_AS_READ: mark_as_read,
    Action.MARK_AS_UNREAD: mark_as_unread,
    Action.MOVE_TO_INBOX: lambda e, g, p: move_message(e, g, {'label_id': 'INBOX'}),
    Action.MOVE_TO_SPAM: lambda e, g, p: move_message(e, g, {'label_id': 'SPAM'}),
    Action.MOVE_TO_TRASH: lambda e, g, p: move_message(e, g, {'label_id': 'TRASH'}),
}

def apply_action(action: Action, email: Email, gmail_service: Any, parameters: Dict[str, Any] = {}) -> None:
    action_func = ACTION_FUNCTIONS.get(action)
    if not action_func:
        raise ValueError(f"Invalid action: {action}")
    action_func(email, gmail_service, parameters)