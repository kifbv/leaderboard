"""Pytest configuration and fixtures."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Set environment variables for testing
os.environ['TABLE_NAME'] = 'leaderboard-test'


@pytest.fixture
def api_gateway_event():
    """Create a basic API Gateway event fixture."""
    return {
        'path': '/api/test',
        'httpMethod': 'GET',
        'headers': {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
        },
        'queryStringParameters': {},
        'pathParameters': {},
        'body': None,
        'isBase64Encoded': False,
        'requestContext': {
            'identity': {
                'sourceIp': '127.0.0.1'
            },
            'authorizer': {
                'claims': {
                    'sub': 'user-123',
                    'email': 'test@example.com',
                    'name': 'Test User',
                    'picture': 'https://example.com/profile.jpg'
                }
            }
        }
    }


@pytest.fixture
def api_gateway_post_event(api_gateway_event):
    """Create a POST API Gateway event fixture."""
    event = api_gateway_event.copy()
    event['httpMethod'] = 'POST'
    event['body'] = json.dumps({
        'test': 'data'
    })
    return event


@pytest.fixture
def dynamodb_mock():
    """Mock DynamoDB resource and table."""
    with patch('boto3.resource') as mock_resource:
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        yield mock_table