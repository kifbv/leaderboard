"""Lambda handler for creating a new game and updating player ratings."""

import json
import logging
from typing import Dict, Any, List, Tuple, Optional

from src.common import (
    success_response,
    error_response,
    parse_event,
    get_item,
    put_item,
    batch_write_items,
    update_item,
    generate_id,
    get_current_timestamp,
    validate_scores,
    format_game_for_dynamo,
    process_game_results,
    GameData
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_player_ratings(player_ids: List[str]) -> Dict[str, int]:
    """Get current ELO ratings for a list of players.
    
    Args:
        player_ids: List of player IDs
        
    Returns:
        Dictionary mapping player IDs to current ratings
    """
    ratings = {}
    
    for player_id in player_ids:
        player = get_item(pk=f"PLAYER#{player_id}", sk="PROFILE")
        if not player:
            raise ValueError(f"Player not found: {player_id}")
        
        ratings[player_id] = player.get('EloScore', 1200)
    
    return ratings


def update_player_ratings(updated_ratings: Dict[str, int]) -> None:
    """Update ELO ratings for multiple players.
    
    Args:
        updated_ratings: Dictionary mapping player IDs to new ratings
    """
    for player_id, new_rating in updated_ratings.items():
        update_item(
            pk=f"PLAYER#{player_id}",
            sk="PROFILE",
            update_expression="SET EloScore = :rating, UpdatedAt = :now",
            expression_values={
                ":rating": new_rating,
                ":now": get_current_timestamp()
            }
        )


def create_game(
    player_ids: List[str],
    scores: List[int],
    site_id: str,
    date: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new game and update player ratings.
    
    Args:
        player_ids: List of player IDs (2 for singles, 4 for doubles)
        scores: List of scores [team1_score, team2_score]
        site_id: Site ID
        date: Optional game date (ISO timestamp)
        
    Returns:
        Created game data with updated player ratings
    """
    # Validate game data
    if len(player_ids) not in [2, 4]:
        raise ValueError("Invalid number of players (must be 2 or 4)")
    
    if not validate_scores(scores, len(player_ids)):
        raise ValueError("Invalid scores format")
    
    # Verify site exists
    site = get_item(pk=f"SITE#{site_id}", sk="DETAILS")
    if not site:
        raise ValueError(f"Site not found: {site_id}")
    
    # Verify players exist and get current ratings
    player_ratings = get_player_ratings(player_ids)
    
    # Generate game ID
    game_id = generate_id("g-")
    
    # Create game data
    now = get_current_timestamp()
    game_data: GameData = {
        'game_id': game_id,
        'site_id': site_id,
        'player_ids': player_ids,
        'scores': scores,
        'date': date or now,
        'created_at': now
    }
    
    # Format for DynamoDB
    game_item, related_items = format_game_for_dynamo(game_data)
    
    # Process game results and update player ratings
    updated_ratings = process_game_results(game_data, player_ratings)
    
    # Write game data to DynamoDB
    put_item(game_item)
    batch_write_items(related_items)
    
    # Update player ratings
    update_player_ratings(updated_ratings)
    
    # Return created game with updated ratings
    return {
        **game_data,
        'updated_ratings': updated_ratings
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for POST /api/games.
    
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
        
        # Extract game data
        player_ids = body.get('player_ids')
        scores = body.get('scores')
        site_id = body.get('site_id')
        date = body.get('date')
        
        # Validate required fields
        if not player_ids:
            return error_response("player_ids is required", 400)
        
        if not scores:
            return error_response("scores is required", 400)
        
        if not site_id:
            return error_response("site_id is required", 400)
        
        # Create game
        game = create_game(
            player_ids=player_ids,
            scores=scores,
            site_id=site_id,
            date=date
        )
        
        return success_response(game, 201)
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return error_response(str(e), 400)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return error_response(f"Error creating game: {str(e)}", 500)


if __name__ == "__main__":
    # For local testing
    test_event = {
        "body": json.dumps({
            "player_ids": ["player1", "player2"],
            "scores": [21, 15],
            "site_id": "site1"
        })
    }
    print(handler(test_event, None))