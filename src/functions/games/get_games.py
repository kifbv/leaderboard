"""Lambda handler for getting recent games."""

import json
import logging
from typing import Dict, Any, List

from src.common import (
    success_response,
    error_response,
    parse_event,
    query_gsi2,
    query_gsi3,
    query_items,
    format_game_from_dynamo
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_recent_games(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent games.
    
    Args:
        limit: Maximum number of games to return
        
    Returns:
        List of game objects
    """
    # Query GSI2 (Type, CreatedAt) to get recent games
    items = query_gsi2(type_value='GAME', limit=limit)
    
    # Format response
    return [format_game_from_dynamo(item) for item in items]


def get_site_games(site_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get games by site ID.
    
    Args:
        site_id: Site ID
        limit: Maximum number of games to return
        
    Returns:
        List of game objects
    """
    # Query GSI3 (SiteId, Type) to get site games
    items = query_gsi3(site_id=site_id, type_value='SITE_GAME', limit=limit)
    
    # Format response
    return [format_game_from_dynamo(item) for item in items]


def get_player_games(player_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get games by player ID.
    
    Args:
        player_id: Player ID
        limit: Maximum number of games to return
        
    Returns:
        List of game objects
    """
    # Query player's games
    items = query_items(
        pk=f"PLAYER#{player_id}",
        sk_begins_with="GAME#",
        limit=limit
    )
    
    # Format response
    return [format_game_from_dynamo(item) for item in items]


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /api/games.
    
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
        query_params = parsed_event['query_parameters']
        
        # Get limit parameter (default to 20, max 100)
        try:
            limit = int(query_params.get('limit', '20'))
            limit = min(max(1, limit), 100)  # Ensure 1 <= limit <= 100
        except ValueError:
            limit = 20
        
        # Get filter parameters
        site_id = query_params.get('site_id')
        player_id = query_params.get('player_id')
        
        # Get games based on parameters
        if player_id:
            games = get_player_games(player_id, limit)
        elif site_id:
            games = get_site_games(site_id, limit)
        else:
            games = get_recent_games(limit)
        
        return success_response(games)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return error_response(f"Error retrieving games: {str(e)}", 500)


if __name__ == "__main__":
    # For local testing
    test_event = {
        "queryStringParameters": {
            "limit": "10"
        }
    }
    print(handler(test_event, None))