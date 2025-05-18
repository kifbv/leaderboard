"""Data models and validation for leaderboard application."""

import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

# Type definitions
class PlayerData(TypedDict):
    player_id: str
    username: str
    email: str
    site_id: str
    elo_score: int
    profile: Dict[str, Any]
    created_at: str
    updated_at: str


class GameData(TypedDict):
    game_id: str
    site_id: str
    player_ids: List[str]
    scores: List[int]
    date: str
    created_at: str


class TournamentData(TypedDict):
    tournament_id: str
    name: str
    site_id: str
    date: str
    player_ids: List[str]
    created_at: str


class SiteData(TypedDict):
    site_id: str
    name: str
    location: str
    created_at: str


# Helper functions for data modeling
def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique ID string
    """
    return f"{prefix}{uuid.uuid4()}"


def get_current_timestamp() -> str:
    """Get current ISO timestamp string.
    
    Returns:
        ISO timestamp string
    """
    return datetime.now().isoformat()


def timestamp_to_dynamo_sk(timestamp: Optional[str] = None) -> str:
    """Convert timestamp to DynamoDB sort key format.
    
    Args:
        timestamp: Optional ISO timestamp string
        
    Returns:
        Sort key string in format 'YYYY-MM-DD#HHMMSS'
    """
    dt = datetime.now() if timestamp is None else datetime.fromisoformat(timestamp)
    return f"{dt.strftime('%Y-%m-%d')}#{dt.strftime('%H%M%S')}"


# Data validation functions
def validate_email(email: str) -> bool:
    """Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Allow alphanumeric, underscore, dash, 3-30 chars
    pattern = r"^[a-zA-Z0-9_-]{3,30}$"
    return bool(re.match(pattern, username))


def validate_scores(scores: List[int], num_players: int) -> bool:
    """Validate game scores based on number of players.
    
    Args:
        scores: List of scores
        num_players: Number of players (2 for singles, 4 for doubles)
        
    Returns:
        True if valid, False otherwise
    """
    if not scores or len(scores) != 2:
        return False
    
    # Scores must be positive integers
    if any(score < 0 for score in scores):
        return False
    
    # Scores cannot be equal (no draws)
    if scores[0] == scores[1]:
        return False
    
    return True


# DynamoDB data formatting functions
def format_player_for_dynamo(player: PlayerData) -> Dict[str, Any]:
    """Format player data for DynamoDB.
    
    Args:
        player: Player data
        
    Returns:
        DynamoDB item dict
    """
    now = get_current_timestamp()
    
    return {
        'PK': f"PLAYER#{player['player_id']}",
        'SK': 'PROFILE',
        'Type': 'PLAYER',
        'PlayerId': player['player_id'],
        'Email': player['email'],
        'Username': player['username'],
        'SiteId': player['site_id'],
        'EloScore': player['elo_score'],
        'Profile': player.get('profile', {}),
        'CreatedAt': player.get('created_at', now),
        'UpdatedAt': now
    }


def format_game_for_dynamo(game: GameData) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Format game data for DynamoDB.
    
    Args:
        game: Game data
        
    Returns:
        Tuple of (game_item, related_items) for DynamoDB
    """
    now = get_current_timestamp()
    game_date = game.get('date', now)
    game_sk = f"GAME#{timestamp_to_dynamo_sk(game_date)}"
    
    # Base game item
    game_item = {
        'PK': f"GAME#{game['game_id']}",
        'SK': game_sk,
        'Type': 'GAME',
        'GameId': game['game_id'],
        'SiteId': game['site_id'],
        'PlayerIds': game['player_ids'],
        'Scores': game['scores'],
        'Date': game_date,
        'CreatedAt': game.get('created_at', now)
    }
    
    # Additional items for player-game relationships
    related_items = []
    for player_id in game['player_ids']:
        related_items.append({
            'PK': f"PLAYER#{player_id}",
            'SK': game_sk,
            'Type': 'PLAYER_GAME',
            'GameId': game['game_id'],
            'SiteId': game['site_id'],
            'PlayerIds': game['player_ids'],
            'Scores': game['scores'],
            'Date': game_date
        })
    
    # Additional item for site-game relationship
    related_items.append({
        'PK': f"SITE#{game['site_id']}",
        'SK': game_sk,
        'Type': 'SITE_GAME',
        'GameId': game['game_id'],
        'PlayerIds': game['player_ids'],
        'Scores': game['scores'],
        'Date': game_date
    })
    
    return game_item, related_items


def format_tournament_for_dynamo(tournament: TournamentData) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Format tournament data for DynamoDB.
    
    Args:
        tournament: Tournament data
        
    Returns:
        Tuple of (tournament_item, related_items) for DynamoDB
    """
    now = get_current_timestamp()
    tournament_date = tournament.get('date', now)
    tournament_sk = f"TOURNAMENT#{timestamp_to_dynamo_sk(tournament_date)}"
    
    # Base tournament item
    tournament_item = {
        'PK': f"TOURNAMENT#{tournament['tournament_id']}",
        'SK': tournament_sk,
        'Type': 'TOURNAMENT',
        'TournamentId': tournament['tournament_id'],
        'Name': tournament['name'],
        'SiteId': tournament['site_id'],
        'Date': tournament_date,
        'PlayerIds': tournament.get('player_ids', []),
        'CreatedAt': tournament.get('created_at', now)
    }
    
    # Additional items for site-tournament relationship
    related_items = [{
        'PK': f"SITE#{tournament['site_id']}",
        'SK': tournament_sk,
        'Type': 'SITE_TOURNAMENT',
        'TournamentId': tournament['tournament_id'],
        'Name': tournament['name'],
        'Date': tournament_date
    }]
    
    return tournament_item, related_items


def format_site_for_dynamo(site: SiteData) -> Dict[str, Any]:
    """Format site data for DynamoDB.
    
    Args:
        site: Site data
        
    Returns:
        DynamoDB item dict
    """
    now = get_current_timestamp()
    
    return {
        'PK': f"SITE#{site['site_id']}",
        'SK': 'DETAILS',
        'Type': 'SITE',
        'SiteId': site['site_id'],
        'Name': site['name'],
        'Location': site['location'],
        'CreatedAt': site.get('created_at', now)
    }


# DynamoDB response formatting functions
def format_player_from_dynamo(item: Dict[str, Any]) -> PlayerData:
    """Format player data from DynamoDB.
    
    Args:
        item: DynamoDB item
        
    Returns:
        Player data
    """
    return {
        'player_id': str(item.get('PlayerId', '')),
        'email': str(item.get('Email', '')),
        'username': str(item.get('Username', '')),
        'site_id': str(item.get('SiteId', '')),
        'elo_score': int(item.get('EloScore', 1200)),
        'profile': dict(item.get('Profile', {})),
        'created_at': str(item.get('CreatedAt', '')),
        'updated_at': str(item.get('UpdatedAt', ''))
    }


def format_game_from_dynamo(item: Dict[str, Any]) -> GameData:
    """Format game data from DynamoDB.
    
    Args:
        item: DynamoDB item
        
    Returns:
        Game data
    """
    return {
        'game_id': str(item.get('GameId', '')),
        'site_id': str(item.get('SiteId', '')),
        'player_ids': list(item.get('PlayerIds', [])),
        'scores': list(item.get('Scores', [])),
        'date': str(item.get('Date', '')),
        'created_at': str(item.get('CreatedAt', ''))
    }


def format_tournament_from_dynamo(item: Dict[str, Any]) -> TournamentData:
    """Format tournament data from DynamoDB.
    
    Args:
        item: DynamoDB item
        
    Returns:
        Tournament data
    """
    return {
        'tournament_id': str(item.get('TournamentId', '')),
        'name': str(item.get('Name', '')),
        'site_id': str(item.get('SiteId', '')),
        'date': str(item.get('Date', '')),
        'player_ids': list(item.get('PlayerIds', [])),
        'created_at': str(item.get('CreatedAt', ''))
    }


def format_site_from_dynamo(item: Dict[str, Any]) -> SiteData:
    """Format site data from DynamoDB.
    
    Args:
        item: DynamoDB item
        
    Returns:
        Site data
    """
    return {
        'site_id': str(item.get('SiteId', '')),
        'name': str(item.get('Name', '')),
        'location': str(item.get('Location', '')),
        'created_at': str(item.get('CreatedAt', ''))
    }