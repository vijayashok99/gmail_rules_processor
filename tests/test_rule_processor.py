import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from src.rules.rule_processor import RuleProcessor
from src.rules.actions import Action
from src.data.models import Email

@pytest.fixture
def sample_rules():
    return {
        "rules": [
            {
                "name": "Mark old emails as unread",
                "predicate": "ALL",
                "conditions": [
                    {
                        "field": "received_date",
                        "predicate": "greater_than",
                        "value": "1 day"
                    }
                ],
                "actions": [
                    {
                        "type": "MARK_AS_UNREAD"
                    }
                ]
            },
            {
                "name": "Move spam to Spam folder",
                "predicate": "ANY",
                "conditions": [
                    {
                        "field": "subject",
                        "predicate": "contains",
                        "value": "spam"
                    },
                    {
                        "field": "sender",
                        "predicate": "contains",
                        "value": "spammer.com"
                    }
                ],
                "actions": [
                    {
                        "type": "MOVE_TO_SPAM"
                    }
                ]
            }
        ]
    }

@pytest.fixture
def rule_processor(sample_rules, tmp_path):
    rules_file = tmp_path / "test_rules.json"
    import json
    with open(rules_file, 'w') as f:
        json.dump(sample_rules, f)
    return RuleProcessor(str(rules_file))

@pytest.fixture
def mock_gmail_service():
    return MagicMock()

def test_rule_processor_initialization(rule_processor):
    assert len(rule_processor.rules) == 2
    assert rule_processor.rules[0]['name'] == "Mark old emails as unread"
    assert rule_processor.rules[1]['name'] == "Move spam to Spam folder"

def test_rule_matches_all_conditions(rule_processor):
    old_email = Email.create(
        message_id='123',
        sender='test@example.com',
        recipient='recipient@example.com',
        subject='Test Email',
        body='This is a test email body',
        received_date=datetime.now(timezone.utc) - timedelta(days=2)
    )
    assert rule_processor.rule_matches(rule_processor.rules[0], old_email)

def test_rule_does_not_match_all_conditions(rule_processor):
    recent_email = Email.create(
        message_id='123',
        sender='test@example.com',
        recipient='recipient@example.com',
        subject='Test Email',
        body='This is a test email body',
        received_date=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    assert not rule_processor.rule_matches(rule_processor.rules[0], recent_email)

def test_rule_matches_any_conditions(rule_processor):
    spam_email = Email.create(
        message_id='123',
        sender='legitimate@example.com',
        recipient='recipient@example.com',
        subject='This is spam',
        body='This is a spam email body',
        received_date=datetime.now(timezone.utc)
    )
    assert rule_processor.rule_matches(rule_processor.rules[1], spam_email)

def test_rule_does_not_match_any_conditions(rule_processor):
    normal_email = Email.create(
        message_id='123',
        sender='legitimate@example.com',
        recipient='recipient@example.com',
        subject='Normal email',
        body='This is a normal email body',
        received_date=datetime.now(timezone.utc)
    )
    assert not rule_processor.rule_matches(rule_processor.rules[1], normal_email)

def test_process_email_applies_action(rule_processor, mock_gmail_service):
    old_email = Email.create(
        message_id='123',
        sender='test@example.com',
        recipient='recipient@example.com',
        subject='Test Email',
        body='This is a test email body',
        received_date=datetime.now(timezone.utc) - timedelta(days=2)
    )
    rule_processor.process_email(old_email, mock_gmail_service)
    mock_gmail_service.mark_as_unread.assert_called_once_with(old_email.message_id)

def test_process_email_does_not_apply_action(rule_processor, mock_gmail_service):
    recent_email = Email.create(
        message_id='123',
        sender='test@example.com',
        recipient='recipient@example.com',
        subject='Test Email',
        body='This is a test email body',
        received_date=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    rule_processor.process_email(recent_email, mock_gmail_service)
    mock_gmail_service.mark_as_unread.assert_not_called()

def test_apply_actions(rule_processor, mock_gmail_service):
    email = Email.create(
        message_id='123',
        sender='spammer@spammer.com',
        recipient='recipient@example.com',
        subject='Spam Email',
        body='This is a spam email body',
        received_date=datetime.now(timezone.utc)
    )
    rule = rule_processor.rules[1]  # "Move spam to Spam folder" rule
    rule_processor.apply_actions(rule, email, mock_gmail_service)
    mock_gmail_service.move_message.assert_called_once_with(email.message_id, 'SPAM')