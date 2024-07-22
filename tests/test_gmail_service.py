import pytest
from src.gmail.gmail_service import GmailService
from unittest.mock import MagicMock

def test_gmail_service_initialization():
    mock_service = MagicMock()
    gmail_service = GmailService(mock_service)
    assert gmail_service.service == mock_service