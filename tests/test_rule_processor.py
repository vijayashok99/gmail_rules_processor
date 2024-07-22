import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from src.rules.rule_processor import RuleProcessor, RuleMatcher
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
def rule_matcher(sample_rules):
    return RuleMatcher(sample_rules['rules'])

@pytest.fixture
def mock_gmail_service():
    return MagicMock()

@pytest.fixture
def rule_processor(rule_matcher, mock_gmail_service):
    return RuleProcessor(rule_matcher, mock_gmail_service)

def test_rule_matcher_initialization(rule_matcher):
    assert len(rule_matcher.rules) == 2
    assert rule_matcher.rules[0]['name'] == "Mark old emails as unread"
    assert rule_matcher.rules[1]['name'] == "Move spam to Spam folder"

def test_rule_matches_all_conditions(rule_matcher):
    old_email = Email.create(
        message_id='123',
        sender='test@example.com',
        recipient='recipient@example.com',
        subject='Test Email',
        body='This is a test email body',
        received_date=datetime.now(timezone.utc) - timedelta(days=2)
    )
    matching_rules = rule_matcher.match(old_email)
    assert len(matching_rules) == 1
    assert matching_rules[0]['name'] == "Mark old emails as unread"

def test_rule_does_not_match_all_conditions(rule_matcher):
    recent_email = Email.create(
        message_id='123',
        sender='test@example.com',
        recipient='recipient@example.com',
        subject='Test Email',
        body='This is a test email body',
        received_date=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    matching_rules = rule_matcher.match(recent_email)
    assert len(matching_rules) == 0

def test_rule_matches_any_conditions(rule_matcher):
    spam_email = Email.create(
        message_id='123',
        sender='legitimate@example.com',
        recipient='recipient@example.com',
        subject='This is spam',
        body='This is a spam email body',
        received_date=datetime.now(timezone.utc)
    )
    matching_rules = rule_matcher.match(spam_email)
    assert len(matching_rules) == 1
    assert matching_rules[0]['name'] == "Move spam to Spam folder"

def test_rule_does_not_match_any_conditions(rule_matcher):
    normal_email = Email.create(
        message_id='123',
        sender='legitimate@example.com',
        recipient='recipient@example.com',
        subject='Normal email',
        body='This is a normal email body',
        received_date=datetime.now(timezone.utc)
    )
    matching_rules = rule_matcher.match(normal_email)
    assert len(matching_rules) == 0

def test_process_email_applies_action(rule_processor):
    old_email = Email.create(
        message_id='123',
        sender='test@example.com',
        recipient='recipient@example.com',
        subject='Test Email',
        body='This is a test email body',
        received_date=datetime.now(timezone.utc) - timedelta(days=2)
    )
    rule_processor.process_email(old_email)
    rule_processor.gmail_service.mark_as_unread.assert_called_once_with(old_email.message_id)

def test_process_email_does_not_apply_action(rule_processor):
    recent_email = Email.create(
        message_id='123',
        sender='test@example.com',
        recipient='recipient@example.com',
        subject='Test Email',
        body='This is a test email body',
        received_date=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    rule_processor.process_email(recent_email)
    rule_processor.gmail_service.mark_as_unread.assert_not_called()

def test_apply_actions(rule_processor):
    email = Email.create(
        message_id='123',
        sender='spammer@spammer.com',
        recipient='recipient@example.com',
        subject='Spam Email',
        body='This is a spam email body',
        received_date=datetime.now(timezone.utc)
    )
    rule = rule_processor.rule_matcher.rules[1]  # "Move spam to Spam folder" rule
    rule_processor.apply_actions(rule, email)
    rule_processor.gmail_service.move_message.assert_called_once_with(email.message_id, 'SPAM')

# Test for RuleProcessor.from_file class method
def test_rule_processor_from_file(sample_rules, tmp_path, mock_gmail_service):
    rules_file = tmp_path / "test_rules.json"
    import json
    with open(rules_file, 'w') as f:
        json.dump(sample_rules, f)
    
    rule_processor = RuleProcessor.from_file(str(rules_file), mock_gmail_service)
    
    assert isinstance(rule_processor, RuleProcessor)
    assert isinstance(rule_processor.rule_matcher, RuleMatcher)
    assert len(rule_processor.rule_matcher.rules) == 2
    assert rule_processor.gmail_service == mock_gmail_service
