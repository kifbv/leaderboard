"""Lambda handler for getting recent tournaments."""

import json
import logging
from typing import Dict, Any, List

from src.common import (
    success_response,
    error_response,
    parse_event,
    query_gsi2,
    query_gsi3,
    format_tournament_from_dynamo
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_recent_tournaments(limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent tournaments.
    
    Args:
        limit: Maximum number of tournaments to return
        
    Returns:
        List of tournament objects
    """
    # Query GSI2 (Type, CreatedAt) to get recent tournaments
    items = query_gsi2(type_value='TOURNAMENT', limit=limit)
    
    # Format response
    return [format_tournament_from_dynamo(item) for item in items]


def get_site_tournaments(site_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get tournaments by site ID.
    
    Args:
        site_id: Site ID
        limit: Maximum number of tournaments to return
        
    Returns:
        List of tournament objects
    """
    # Query GSI3 (SiteId, Type) to get site tournaments
    items = query_gsi3(site_id=site_id, type_value='SITE_TOURNAMENT', limit=limit)
    
    # Format response
    return [format_tournament_from_dynamo(item) for item in items]


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /api/tournaments.
    
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
        
        # Get limit parameter (default to 5, max 20)
        try:
            limit = int(query_params.get('limit', '5'))
            limit = min(max(1, limit), 20)  # Ensure 1 <= limit <= 20
        except ValueError:
            limit = 5
        
        # Get site_id parameter
        site_id = query_params.get('site_id')
        
        # Get tournaments based on parameters
        if site_id:
            tournaments = get_site_tournaments(site_id, limit)
        else:
            tournaments = get_recent_tournaments(limit)
        
        return success_response(tournaments)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return error_response(f"Error retrieving tournaments: {str(e)}", 500)


if __name__ == "__main__":
    # For local testing
    test_event = {
        "queryStringParameters": {
            "limit": "5"
        }
    }
    print(handler(test_event, None))