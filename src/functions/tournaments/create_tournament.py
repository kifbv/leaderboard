"""Lambda handler for creating a new tournament (admin only)."""

import json
import logging
from typing import Dict, Any, List, Optional

from src.common import (
    success_response,
    error_response,
    parse_event,
    get_item,
    put_item,
    batch_write_items,
    generate_id,
    format_tournament_for_dynamo,
    TournamentData
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_tournament(
    name: str,
    site_id: str,
    player_ids: List[str],
    date: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new tournament.
    
    Args:
        name: Tournament name
        site_id: Site ID
        player_ids: List of player IDs for participants
        date: Optional tournament date (ISO timestamp)
        
    Returns:
        Created tournament data
    """
    # Verify site exists
    site = get_item(pk=f"SITE#{site_id}", sk="DETAILS")
    if not site:
        raise ValueError(f"Site not found: {site_id}")
    
    # Verify players exist
    for player_id in player_ids:
        player = get_item(pk=f"PLAYER#{player_id}", sk="PROFILE")
        if not player:
            raise ValueError(f"Player not found: {player_id}")
    
    # Generate tournament ID
    tournament_id = generate_id("t-")
    
    # Get current timestamp
    from datetime import datetime
    now = datetime.now().isoformat()
    
    # Create tournament data
    tournament_data: TournamentData = {
        'tournament_id': tournament_id,
        'name': name,
        'site_id': site_id,
        'player_ids': player_ids,
        'date': date or now,
        'created_at': now
    }
    
    # Format for DynamoDB
    tournament_item, related_items = format_tournament_for_dynamo(tournament_data)
    
    # Write to DynamoDB
    put_item(tournament_item)
    batch_write_items(related_items)
    
    return tournament_data


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for POST /api/tournaments.
    
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
        body = parsed_event['body']
        
        # Validate request body
        if not body:
            return error_response("Request body is required", 400)
        
        # Extract tournament data
        name = body.get('name')
        site_id = body.get('site_id')
        player_ids = body.get('player_ids', [])
        date = body.get('date')
        
        # Validate required fields
        if not name:
            return error_response("name is required", 400)
        
        if not site_id:
            return error_response("site_id is required", 400)
        
        # Create tournament
        tournament = create_tournament(name, site_id, player_ids, date)
        
        return success_response(tournament, 201)
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return error_response(str(e), 400)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return error_response(f"Error creating tournament: {str(e)}", 500)


if __name__ == "__main__":
    # For local testing
    test_event = {
        "body": json.dumps({
            "name": "Summer Championship 2023",
            "site_id": "site1",
            "player_ids": ["player1", "player2", "player3", "player4"]
        })
    }
    print(handler(test_event, None))