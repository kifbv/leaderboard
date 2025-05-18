"""Test the get_players lambda function."""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.functions.players.get_players import handler, get_top_players, get_site_players


@patch('src.functions.players.get_players.query_gsi2')
def test_get_top_players(mock_query_gsi2):
    """Test getting top players by ELO score."""
    # Setup mock data
    mock_items = [
        {
            'PK': 'PLAYER#p-1',
            'SK': 'PROFILE',
            'Type': 'PLAYER',
            'PlayerId': 'p-1',
            'Username': 'player1',
            'Email': 'player1@example.com',
            'SiteId': 'site-1',
            'EloScore': 1500,
            'Profile': {},
            'CreatedAt': '2023-01-01T00:00:00',
            'UpdatedAt': '2023-01-01T00:00:00'
        },
        {
            'PK': 'PLAYER#p-2',
            'SK': 'PROFILE',
            'Type': 'PLAYER',
            'PlayerId': 'p-2',
            'Username': 'player2',
            'Email': 'player2@example.com',
            'SiteId': 'site-1',
            'EloScore': 1400,
            'Profile': {},
            'CreatedAt': '2023-01-01T00:00:00',
            'UpdatedAt': '2023-01-01T00:00:00'
        }
    ]
    mock_query_gsi2.return_value = mock_items
    
    # Call function
    result = get_top_players(limit=10)
    
    # Verify
    mock_query_gsi2.assert_called_once_with(type_value='PLAYER', limit=10)
    assert len(result) == 2
    assert result[0]['player_id'] == 'p-1'
    assert result[0]['elo_score'] == 1500
    assert result[1]['player_id'] == 'p-2'
    assert result[1]['elo_score'] == 1400


@patch('src.functions.players.get_players.query_gsi3')
def test_get_site_players(mock_query_gsi3):
    """Test getting players by site ID."""
    # Setup mock data
    mock_items = [
        {
            'PK': 'PLAYER#p-1',
            'SK': 'PROFILE',
            'Type': 'PLAYER',
            'PlayerId': 'p-1',
            'Username': 'player1',
            'Email': 'player1@example.com',
            'SiteId': 'site-1',
            'EloScore': 1500,
            'Profile': {},
            'CreatedAt': '2023-01-01T00:00:00',
            'UpdatedAt': '2023-01-01T00:00:00'
        }
    ]
    mock_query_gsi3.return_value = mock_items
    
    # Call function
    result = get_site_players(site_id='site-1', limit=10)
    
    # Verify
    mock_query_gsi3.assert_called_once_with(site_id='site-1', type_value='PLAYER', limit=10)
    assert len(result) == 1
    assert result[0]['player_id'] == 'p-1'
    assert result[0]['site_id'] == 'site-1'


@patch('src.functions.players.get_players.get_top_players')
@patch('src.functions.players.get_players.get_site_players')
def test_handler_top_players(mock_get_site_players, mock_get_top_players):
    """Test the Lambda handler for getting top players."""
    # Setup mock data
    mock_players = [
        {
            'player_id': 'p-1',
            'username': 'player1',
            'email': 'player1@example.com',
            'site_id': 'site-1',
            'elo_score': 1500,
            'profile': {},
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
    ]
    mock_get_top_players.return_value = mock_players
    
    # Mock API Gateway event
    event = {
        'queryStringParameters': {
            'limit': '5'
        }
    }
    
    # Call handler
    response = handler(event, {})
    
    # Verify
    mock_get_top_players.assert_called_once_with(limit=5)
    mock_get_site_players.assert_not_called()
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body) == 1
    assert body[0]['player_id'] == 'p-1'


@patch('src.functions.players.get_players.get_top_players')
@patch('src.functions.players.get_players.get_site_players')
def test_handler_site_players(mock_get_site_players, mock_get_top_players):
    """Test the Lambda handler for getting players by site."""
    # Setup mock data
    mock_players = [
        {
            'player_id': 'p-1',
            'username': 'player1',
            'email': 'player1@example.com',
            'site_id': 'site-1',
            'elo_score': 1500,
            'profile': {},
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
    ]
    mock_get_site_players.return_value = mock_players
    
    # Mock API Gateway event
    event = {
        'queryStringParameters': {
            'site_id': 'site-1',
            'limit': '10'
        }
    }
    
    # Call handler
    response = handler(event, {})
    
    # Verify
    mock_get_site_players.assert_called_once_with(site_id='site-1', limit=10)
    mock_get_top_players.assert_not_called()
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body) == 1
    assert body[0]['player_id'] == 'p-1'
    assert body[0]['site_id'] == 'site-1'


@patch('src.functions.players.get_players.get_top_players')
def test_handler_error(mock_get_top_players):
    """Test the Lambda handler when an error occurs."""
    # Setup mock to raise exception
    mock_get_top_players.side_effect = Exception("Test error")
    
    # Mock API Gateway event
    event = {
        'queryStringParameters': {
            'limit': '10'
        }
    }
    
    # Call handler
    response = handler(event, {})
    
    # Verify
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'message' in body
    assert 'Error retrieving players' in body['message']