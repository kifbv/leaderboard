"""Lambda handler for creating a new player."""

import json
import logging
from typing import Dict, Any, List, Optional

from src.common import (
    success_response,
    error_response,
    parse_event,
    get_item,
    put_item,
    generate_id,
    get_current_timestamp,
    DEFAULT_RATING,
    validate_email,
    validate_username,
    format_player_for_dynamo,
    PlayerData
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_player(
    username: str, 
    email: str, 
    site_id: str,
    user_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new player.
    
    Args:
        username: Player username
        email: Player email
        site_id: Site ID
        user_info: Optional user info from authentication
        
    Returns:
        Created player data
    """
    # Validate player data
    if not validate_username(username):
        raise ValueError("Invalid username format")
    
    if not validate_email(email):
        raise ValueError("Invalid email format")
    
    # Verify site exists
    site = get_item(pk=f"SITE#{site_id}", sk="DETAILS")
    if not site:
        raise ValueError(f"Site not found: {site_id}")
    
    # Check if player with this email already exists
    # Note: In a production system, we would use a GSI to check this,
    #       but for simplicity we're focusing on the core functionality
    
    # Generate player ID
    player_id = generate_id("p-")
    
    # Create player data
    now = get_current_timestamp()
    player_data: PlayerData = {
        'player_id': player_id,
        'username': username,
        'email': email,
        'site_id': site_id,
        'elo_score': DEFAULT_RATING,
        'profile': {
            'picture': user_info.get('picture') if user_info else None,
            'name': user_info.get('name') if user_info else username
        },
        'created_at': now,
        'updated_at': now
    }
    
    # Format for DynamoDB
    player_item = format_player_for_dynamo(player_data)
    
    # Write to DynamoDB
    put_item(player_item)
    
    return player_data


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for POST /api/players.
    
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
        user_info = parsed_event['user']
        
        # Validate request body
        if not body:
            return error_response("Request body is required", 400)
        
        # Extract player data
        username = body.get('username')
        email = body.get('email') or user_info.get('email')
        site_id = body.get('site_id')
        
        # Validate required fields
        if not username:
            return error_response("Username is required", 400)
        
        if not email:
            return error_response("Email is required", 400)
        
        if not site_id:
            return error_response("Site ID is required", 400)
        
        # Create player
        player = create_player(username, email, site_id, user_info)
        
        return success_response(player, 201)
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return error_response(str(e), 400)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return error_response(f"Error creating player: {str(e)}", 500)


if __name__ == "__main__":
    # For local testing
    test_event = {
        "body": json.dumps({
            "username": "testplayer",
            "email": "test@example.com",
            "site_id": "example-site-id"
        })
    }
    print(handler(test_event, None))