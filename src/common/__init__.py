"""Common utilities package for leaderboard application."""

from .api import (
    build_response,
    success_response,
    error_response,
    parse_event
)

from .dynamodb import (
    get_item,
    query_items,
    query_gsi1,
    query_gsi2,
    query_gsi3,
    put_item,
    update_item,
    batch_write_items
)

from .elo import (
    DEFAULT_RATING,
    calculate_expected_score,
    calculate_new_rating,
    update_ratings_for_singles_game,
    update_ratings_for_doubles_game,
    process_game_results
)

from .models import (
    # Type definitions
    PlayerData,
    GameData,
    TournamentData,
    SiteData,
    
    # Helper functions
    generate_id,
    get_current_timestamp,
    timestamp_to_dynamo_sk,
    
    # Validation functions
    validate_email,
    validate_username,
    validate_scores,
    
    # DynamoDB formatting functions
    format_player_for_dynamo,
    format_game_for_dynamo,
    format_tournament_for_dynamo,
    format_site_for_dynamo,
    
    # Response formatting functions
    format_player_from_dynamo,
    format_game_from_dynamo,
    format_tournament_from_dynamo,
    format_site_from_dynamo
)

# Define explicitly exported symbols
__all__ = [
    'build_response', 'success_response', 'error_response', 'parse_event',
    'get_item', 'query_items', 'query_gsi1', 'query_gsi2', 'query_gsi3',
    'put_item', 'update_item', 'batch_write_items',
    'DEFAULT_RATING', 'calculate_expected_score', 'calculate_new_rating',
    'update_ratings_for_singles_game', 'update_ratings_for_doubles_game',
    'process_game_results',
    'PlayerData', 'GameData', 'TournamentData', 'SiteData',
    'generate_id', 'get_current_timestamp', 'timestamp_to_dynamo_sk',
    'validate_email', 'validate_username', 'validate_scores',
    'format_player_for_dynamo', 'format_game_for_dynamo',
    'format_tournament_for_dynamo', 'format_site_for_dynamo',
    'format_player_from_dynamo', 'format_game_from_dynamo',
    'format_tournament_from_dynamo', 'format_site_from_dynamo'
]