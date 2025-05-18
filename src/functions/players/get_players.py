"""Lambda handler for getting top players or players by site."""

import json
import logging
from typing import Dict, Any, List

from src.common import (
    success_response,
    error_response,
    parse_event,
    query_gsi2,
    query_gsi3,
    format_player_from_dynamo
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_top_players(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top players by ELO score.
    
    Args:
        limit: Maximum number of players to return
        
    Returns:
        List of player objects
    """
    # Query GSI2 (Type, EloScore) to get top players
    items = query_gsi2(type_value='PLAYER', limit=limit)
    
    # Format response
    return [format_player_from_dynamo(item) for item in items]


def get_site_players(site_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get players by site ID.
    
    Args:
        site_id: Site ID
        limit: Maximum number of players to return
        
    Returns:
        List of player objects
    """
    # Query GSI3 (SiteId, Type) to get site players
    items = query_gsi3(site_id=site_id, type_value='PLAYER', limit=limit)
    
    # Format response
    return [format_player_from_dynamo(item) for item in items]


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /api/players.
    
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
        
        # Get limit parameter (default to 10, max 100)
        try:
            limit = int(query_params.get('limit', '10'))
            limit = min(max(1, limit), 100)  # Ensure 1 <= limit <= 100
        except ValueError:
            limit = 10
        
        # Get site_id parameter
        site_id = query_params.get('site_id')
        
        # Get players based on parameters
        if site_id:
            players = get_site_players(site_id=site_id, limit=limit)
        else:
            players = get_top_players(limit=limit)
        
        return success_response(players)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return error_response(f"Error retrieving players: {str(e)}", 500)


if __name__ == "__main__":
    # For local testing
    test_event = {
        "queryStringParameters": {
            "limit": "10"
        }
    }
    print(handler(test_event, None))