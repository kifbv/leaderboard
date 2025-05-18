"""Test the data models and validation functions."""

import re
import uuid
from datetime import datetime
import pytest

from src.common.models import (
    validate_email,
    validate_username,
    validate_scores,
    generate_id,
    get_current_timestamp,
    timestamp_to_dynamo_sk,
    format_player_for_dynamo,
    format_game_for_dynamo,
    format_tournament_for_dynamo,
    format_site_for_dynamo,
    format_player_from_dynamo,
    format_game_from_dynamo,
    format_tournament_from_dynamo,
    format_site_from_dynamo
)


class TestValidationFunctions:
    """Test validation functions for data models."""
    
    def test_validate_email(self):
        """Test email validation function."""
        # Valid emails
        assert validate_email("user@example.com") is True
        assert validate_email("user.name+tag@example.co.uk") is True
        assert validate_email("user123@subdomain.example.org") is True
        
        # Invalid emails
        assert validate_email("not_an_email") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user@.com") is False
        assert validate_email("user@example.") is False
    
    def test_validate_username(self):
        """Test username validation function."""
        # Valid usernames
        assert validate_username("user123") is True
        assert validate_username("user_name") is True
        assert validate_username("user-name") is True
        assert validate_username("123456") is True
        
        # Invalid usernames
        assert validate_username("ab") is False  # Too short
        assert validate_username("a" * 31) is False  # Too long
        assert validate_username("user name") is False  # Contains space
        assert validate_username("user@name") is False  # Contains special char
    
    def test_validate_scores(self):
        """Test game scores validation function."""
        # Valid scores for singles game
        assert validate_scores([21, 15], 2) is True
        assert validate_scores([15, 21], 2) is True
        assert validate_scores([0, 10], 2) is True
        
        # Valid scores for doubles game
        assert validate_scores([21, 15], 4) is True
        
        # Invalid scores
        assert validate_scores([21, 21], 2) is False  # Tie not allowed
        assert validate_scores([21], 2) is False  # Not enough scores
        assert validate_scores([21, 15, 10], 2) is False  # Too many scores
        assert validate_scores([-1, 10], 2) is False  # Negative score
        assert validate_scores([], 2) is False  # Empty list


class TestHelperFunctions:
    """Test helper functions for data models."""
    
    def test_generate_id(self):
        """Test ID generation function."""
        # Default prefix
        id1 = generate_id()
        assert isinstance(id1, str)
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', id1)
        
        # Custom prefix
        id2 = generate_id("test-")
        assert id2.startswith("test-")
        assert re.match(r'^test-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', id2)
        
        # IDs should be unique
        assert generate_id() != generate_id()
    
    def test_get_current_timestamp(self):
        """Test timestamp generation function."""
        timestamp = get_current_timestamp()
        assert isinstance(timestamp, str)
        
        # Should be ISO format
        try:
            dt = datetime.fromisoformat(timestamp)
            assert isinstance(dt, datetime)
        except ValueError:
            pytest.fail("Timestamp is not in valid ISO format")
    
    def test_timestamp_to_dynamo_sk(self):
        """Test conversion of timestamp to DynamoDB sort key format."""
        # With provided timestamp
        iso_timestamp = "2023-05-15T14:30:45.123456"
        dynamo_sk = timestamp_to_dynamo_sk(iso_timestamp)
        assert dynamo_sk == "2023-05-15#143045"
        
        # Without timestamp (uses current time)
        dynamo_sk = timestamp_to_dynamo_sk()
        assert isinstance(dynamo_sk, str)
        assert re.match(r'^\d{4}-\d{2}-\d{2}#\d{6}$', dynamo_sk)


class TestFormatFunctions:
    """Test formatting functions for DynamoDB."""
    
    def test_format_player_for_dynamo(self):
        """Test formatting player data for DynamoDB."""
        player_data = {
            'player_id': 'p-123',
            'username': 'testuser',
            'email': 'test@example.com',
            'site_id': 'site-1',
            'elo_score': 1200,
            'profile': {'name': 'Test User'},
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        
        # Format for DynamoDB
        item = format_player_for_dynamo(player_data)
        
        # Check fields
        assert item['PK'] == 'PLAYER#p-123'
        assert item['SK'] == 'PROFILE'
        assert item['Type'] == 'PLAYER'
        assert item['PlayerId'] == 'p-123'
        assert item['Username'] == 'testuser'
        assert item['Email'] == 'test@example.com'
        assert item['SiteId'] == 'site-1'
        assert item['EloScore'] == 1200
        assert item['Profile'] == {'name': 'Test User'}
    
    def test_format_game_for_dynamo(self):
        """Test formatting game data for DynamoDB."""
        game_data = {
            'game_id': 'g-123',
            'site_id': 'site-1',
            'player_ids': ['p-1', 'p-2'],
            'scores': [21, 15],
            'date': '2023-01-01T12:00:00',
            'created_at': '2023-01-01T12:00:00'
        }
        
        # Format for DynamoDB
        game_item, related_items = format_game_for_dynamo(game_data)
        
        # Check main item
        assert game_item['PK'] == 'GAME#g-123'
        assert game_item['SK'].startswith('GAME#2023-01-01#')
        assert game_item['Type'] == 'GAME'
        assert game_item['GameId'] == 'g-123'
        assert game_item['SiteId'] == 'site-1'
        assert game_item['PlayerIds'] == ['p-1', 'p-2']
        assert game_item['Scores'] == [21, 15]
        
        # Check related items
        assert len(related_items) == 3  # 2 players + 1 site
        
        # Player items
        player_items = [item for item in related_items if item['PK'].startswith('PLAYER#')]
        assert len(player_items) == 2
        assert player_items[0]['PK'] == 'PLAYER#p-1'
        assert player_items[1]['PK'] == 'PLAYER#p-2'
        
        # Site item
        site_items = [item for item in related_items if item['PK'].startswith('SITE#')]
        assert len(site_items) == 1
        assert site_items[0]['PK'] == 'SITE#site-1'


class TestFromDynamoFunctions:
    """Test functions that format DynamoDB responses to application models."""
    
    def test_format_player_from_dynamo(self):
        """Test formatting player data from DynamoDB."""
        dynamo_item = {
            'PK': 'PLAYER#p-123',
            'SK': 'PROFILE',
            'Type': 'PLAYER',
            'PlayerId': 'p-123',
            'Username': 'testuser',
            'Email': 'test@example.com',
            'SiteId': 'site-1',
            'EloScore': 1200,
            'Profile': {'name': 'Test User'},
            'CreatedAt': '2023-01-01T00:00:00',
            'UpdatedAt': '2023-01-01T00:00:00'
        }
        
        player = format_player_from_dynamo(dynamo_item)
        
        assert player['player_id'] == 'p-123'
        assert player['username'] == 'testuser'
        assert player['email'] == 'test@example.com'
        assert player['site_id'] == 'site-1'
        assert player['elo_score'] == 1200
        assert player['profile'] == {'name': 'Test User'}
        assert player['created_at'] == '2023-01-01T00:00:00'
        assert player['updated_at'] == '2023-01-01T00:00:00'
    
    def test_format_game_from_dynamo(self):
        """Test formatting game data from DynamoDB."""
        dynamo_item = {
            'PK': 'GAME#g-123',
            'SK': 'GAME#2023-01-01#120000',
            'Type': 'GAME',
            'GameId': 'g-123',
            'SiteId': 'site-1',
            'PlayerIds': ['p-1', 'p-2'],
            'Scores': [21, 15],
            'Date': '2023-01-01T12:00:00',
            'CreatedAt': '2023-01-01T12:00:00'
        }
        
        game = format_game_from_dynamo(dynamo_item)
        
        assert game['game_id'] == 'g-123'
        assert game['site_id'] == 'site-1'
        assert game['player_ids'] == ['p-1', 'p-2']
        assert game['scores'] == [21, 15]
        assert game['date'] == '2023-01-01T12:00:00'
        assert game['created_at'] == '2023-01-01T12:00:00'