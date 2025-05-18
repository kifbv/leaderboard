"""Lambda handler for getting a player's profile."""

import json
import logging
from typing import Dict, Any, List, Optional

from src.common import (
    success_response,
    error_response,
    parse_event,
    get_item,
    query_items,
    format_player_from_dynamo,
    format_game_from_dynamo
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_player_profile(player_id: str) -> Optional[Dict[str, Any]]:
    """Get a player's profile.
    
    Args:
        player_id: Player ID
        
    Returns:
        Player profile or None if not found
    """
    # Get player profile
    item = get_item(pk=f"PLAYER#{player_id}", sk="PROFILE")
    
    if not item:
        return None
    
    return format_player_from_dynamo(item)


def get_player_recent_games(player_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get a player's recent games.
    
    Args:
        player_id: Player ID
        limit: Maximum number of games to return
        
    Returns:
        List of game objects
    """
    # Query player's recent games
    items = query_items(
        pk=f"PLAYER#{player_id}",
        sk_begins_with="GAME#",
        limit=limit
    )
    
    # Format response
    return [format_game_from_dynamo(item) for item in items]


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /api/players/{id}.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    logger.info(f"Processing event: {json.dumps(event)}")
    
    try:
        # Parse event
        parsed_event = parse_event(event)
        path_params = parsed_event['path_parameters']
        query_params = parsed_event['query_parameters']
        
        # Get player ID
        player_id = path_params.get('id')
        if not player_id:
            return error_response("Player ID is required", 400)
        
        # Get limit parameter (default to 20, max 100)
        try:
            limit = int(query_params.get('limit', '20'))
            limit = min(max(1, limit), 100)  # Ensure 1 <= limit <= 100
        except ValueError:
            limit = 20
        
        # Get player profile
        player = get_player_profile(player_id)
        if not player:
            return error_response(f"Player not found: {player_id}", 404)
        
        # Get player's recent games
        recent_games = get_player_recent_games(player_id, limit)
        
        # Combine profile and recent games
        result = {
            **player,
            "recent_games": recent_games
        }
        
        return success_response(result)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return error_response(f"Error retrieving player profile: {str(e)}", 500)


if __name__ == "__main__":
    # For local testing
    test_event = {
        "pathParameters": {
            "id": "example-player-id"
        },
        "queryStringParameters": {
            "limit": "10"
        }
    }
    print(handler(test_event, None))