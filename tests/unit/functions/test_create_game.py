"""Test the create_game lambda function."""

import json
import pytest
from unittest.mock import patch, MagicMock, call

from src.functions.games.create_game import (
    handler, create_game, get_player_ratings, update_player_ratings
)


@patch('src.functions.games.create_game.get_item')
def test_get_player_ratings(mock_get_item):
    """Test getting current ELO ratings for players."""
    # Setup mock responses
    mock_get_item.side_effect = [
        # First player
        {
            'PK': 'PLAYER#p-1',
            'SK': 'PROFILE',
            'PlayerId': 'p-1',
            'EloScore': 1200
        },
        # Second player
        {
            'PK': 'PLAYER#p-2',
            'SK': 'PROFILE',
            'PlayerId': 'p-2',
            'EloScore': 1300
        }
    ]
    
    # Call function
    player_ids = ['p-1', 'p-2']
    ratings = get_player_ratings(player_ids)
    
    # Verify
    assert mock_get_item.call_count == 2
    mock_get_item.assert_has_calls([
        call(pk='PLAYER#p-1', sk='PROFILE'),
        call(pk='PLAYER#p-2', sk='PROFILE')
    ])
    
    assert ratings == {
        'p-1': 1200,
        'p-2': 1300
    }


@patch('src.functions.games.create_game.get_item')
def test_get_player_ratings_not_found(mock_get_item):
    """Test exception when player is not found."""
    # Setup mock to return None (player not found)
    mock_get_item.return_value = None
    
    # Call function
    player_ids = ['p-1']
    
    # Verify exception is raised
    with pytest.raises(ValueError, match="Player not found: p-1"):
        get_player_ratings(player_ids)


@patch('src.functions.games.create_game.update_item')
@patch('src.functions.games.create_game.get_current_timestamp')
def test_update_player_ratings(mock_get_current_timestamp, mock_update_item):
    """Test updating player ratings in DynamoDB."""
    # Setup mock
    mock_get_current_timestamp.return_value = "2023-01-01T00:00:00"
    
    # Call function
    updated_ratings = {
        'p-1': 1250,
        'p-2': 1150
    }
    update_player_ratings(updated_ratings)
    
    # Verify
    assert mock_update_item.call_count == 2
    mock_update_item.assert_has_calls([
        call(
            pk='PLAYER#p-1',
            sk='PROFILE',
            update_expression='SET EloScore = :rating, UpdatedAt = :now',
            expression_values={
                ':rating': 1250,
                ':now': "2023-01-01T00:00:00"
            }
        ),
        call(
            pk='PLAYER#p-2',
            sk='PROFILE',
            update_expression='SET EloScore = :rating, UpdatedAt = :now',
            expression_values={
                ':rating': 1150,
                ':now': "2023-01-01T00:00:00"
            }
        )
    ], any_order=True)


@patch('src.functions.games.create_game.validate_scores')
@patch('src.functions.games.create_game.get_item')
@patch('src.functions.games.create_game.get_player_ratings')
@patch('src.functions.games.create_game.format_game_for_dynamo')
@patch('src.functions.games.create_game.process_game_results')
@patch('src.functions.games.create_game.put_item')
@patch('src.functions.games.create_game.batch_write_items')
@patch('src.functions.games.create_game.update_player_ratings')
@patch('src.functions.games.create_game.generate_id')
@patch('src.functions.games.create_game.get_current_timestamp')
def test_create_game(
    mock_get_current_timestamp,
    mock_generate_id,
    mock_update_player_ratings,
    mock_batch_write_items,
    mock_put_item,
    mock_process_game_results,
    mock_format_game_for_dynamo,
    mock_get_player_ratings,
    mock_get_item,
    mock_validate_scores
):
    """Test creating a new game and updating player ratings."""
    # Setup mocks
    mock_validate_scores.return_value = True
    mock_get_item.return_value = {'SiteId': 'site-1'}  # Site exists
    mock_get_player_ratings.return_value = {'p-1': 1200, 'p-2': 1200}
    mock_format_game_for_dynamo.return_value = (
        {'PK': 'GAME#g-123', 'SK': 'GAME#2023-01-01#000000'},  # Game item
        [{'PK': 'PLAYER#p-1'}, {'PK': 'PLAYER#p-2'}, {'PK': 'SITE#site-1'}]  # Related items
    )
    mock_process_game_results.return_value = {'p-1': 1216, 'p-2': 1184}
    mock_generate_id.return_value = 'g-123'
    mock_get_current_timestamp.return_value = '2023-01-01T00:00:00'
    
    # Call function
    result = create_game(
        player_ids=['p-1', 'p-2'],
        scores=[21, 15],
        site_id='site-1'
    )
    
    # Verify
    mock_validate_scores.assert_called_once_with([21, 15], 2)
    mock_get_item.assert_called_once_with(pk='SITE#site-1', sk='DETAILS')
    mock_get_player_ratings.assert_called_once_with(['p-1', 'p-2'])
    
    expected_game_data = {
        'game_id': 'g-123',
        'site_id': 'site-1',
        'player_ids': ['p-1', 'p-2'],
        'scores': [21, 15],
        'date': '2023-01-01T00:00:00',
        'created_at': '2023-01-01T00:00:00'
    }
    mock_format_game_for_dynamo.assert_called_once()
    
    mock_put_item.assert_called_once()
    mock_batch_write_items.assert_called_once()
    mock_update_player_ratings.assert_called_once_with({'p-1': 1216, 'p-2': 1184})
    
    # Check result
    assert result['game_id'] == 'g-123'
    assert result['player_ids'] == ['p-1', 'p-2']
    assert result['scores'] == [21, 15]
    assert result['updated_ratings'] == {'p-1': 1216, 'p-2': 1184}


@patch('src.functions.games.create_game.create_game')
def test_handler_success(mock_create_game):
    """Test the Lambda handler for creating a game (success case)."""
    # Setup mock
    mock_create_game.return_value = {
        'game_id': 'g-123',
        'site_id': 'site-1',
        'player_ids': ['p-1', 'p-2'],
        'scores': [21, 15],
        'date': '2023-01-01T00:00:00',
        'updated_ratings': {'p-1': 1216, 'p-2': 1184}
    }
    
    # Mock API Gateway event
    event = {
        'body': json.dumps({
            'player_ids': ['p-1', 'p-2'],
            'scores': [21, 15],
            'site_id': 'site-1'
        })
    }
    
    # Call handler
    response = handler(event, {})
    
    # Verify
    mock_create_game.assert_called_once_with(
        player_ids=['p-1', 'p-2'], 
        scores=[21, 15], 
        site_id='site-1',
        date=None
    )
    
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['game_id'] == 'g-123'
    assert body['updated_ratings'] == {'p-1': 1216, 'p-2': 1184}


@patch('src.functions.games.create_game.create_game')
def test_handler_validation_error(mock_create_game):
    """Test the Lambda handler with validation error."""
    # Setup mock to raise ValueError
    mock_create_game.side_effect = ValueError("Invalid scores format")
    
    # Mock API Gateway event
    event = {
        'body': json.dumps({
            'player_ids': ['p-1', 'p-2'],
            'scores': [21, 21],  # Invalid scores (tie)
            'site_id': 'site-1'
        })
    }
    
    # Call handler
    response = handler(event, {})
    
    # Verify
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['message'] == 'Invalid scores format'