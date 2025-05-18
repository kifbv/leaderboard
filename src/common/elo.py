"""ELO rating system for ping-pong leaderboard."""

from typing import Any, Dict, List, Tuple

# Constants for ELO calculation
DEFAULT_K_FACTOR = 32  # Standard K-factor for chess
DEFAULT_RATING = 1200  # Default starting rating for new players


def calculate_expected_score(player_rating: int, opponent_rating: float) -> float:
    """Calculate the expected score for a player.
    
    Args:
        player_rating: Player's current ELO rating
        opponent_rating: Opponent's current ELO rating
        
    Returns:
        Expected score (between 0 and 1)
    """
    return 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))


def calculate_new_rating(
    player_rating: int, 
    opponent_rating: int, 
    actual_score: float,
    k_factor: int = DEFAULT_K_FACTOR
) -> int:
    """Calculate the new ELO rating for a player.
    
    Args:
        player_rating: Player's current ELO rating
        opponent_rating: Opponent's current ELO rating
        actual_score: Actual score (1 for win, 0.5 for draw, 0 for loss)
        k_factor: K-factor for ELO calculation
        
    Returns:
        New ELO rating
    """
    expected_score = calculate_expected_score(player_rating, opponent_rating)
    new_rating = player_rating + k_factor * (actual_score - expected_score)
    return round(new_rating)


def update_ratings_for_singles_game(
    player1_rating: int, 
    player2_rating: int, 
    player1_won: bool,
    k_factor: int = DEFAULT_K_FACTOR
) -> Tuple[int, int]:
    """Update ELO ratings for a singles game.
    
    Args:
        player1_rating: Player 1's current ELO rating
        player2_rating: Player 2's current ELO rating
        player1_won: True if player 1 won, False if player 2 won
        k_factor: K-factor for ELO calculation
        
    Returns:
        Tuple of (player1_new_rating, player2_new_rating)
    """
    player1_score = 1.0 if player1_won else 0.0
    player2_score = 1.0 - player1_score
    
    player1_new_rating = calculate_new_rating(
        player1_rating, player2_rating, player1_score, k_factor
    )
    player2_new_rating = calculate_new_rating(
        player2_rating, player1_rating, player2_score, k_factor
    )
    
    return player1_new_rating, player2_new_rating


def update_ratings_for_doubles_game(
    team1_ratings: Tuple[int, int],
    team2_ratings: Tuple[int, int],
    team1_won: bool,
    k_factor: int = DEFAULT_K_FACTOR
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Update ELO ratings for a doubles game.
    
    Args:
        team1_ratings: Tuple of (player1_rating, player2_rating) for team 1
        team2_ratings: Tuple of (player1_rating, player2_rating) for team 2
        team1_won: True if team 1 won, False if team 2 won
        k_factor: K-factor for ELO calculation
        
    Returns:
        Tuple of (team1_new_ratings, team2_new_ratings)
    """
    # Calculate average ratings for each team
    team1_avg_rating = sum(team1_ratings) / 2
    team2_avg_rating = sum(team2_ratings) / 2
    
    team1_score = 1.0 if team1_won else 0.0
    team2_score = 1.0 - team1_score
    
    # Calculate expected scores for each player against the average of the opposing team
    player1_expected = calculate_expected_score(team1_ratings[0], team2_avg_rating)
    player2_expected = calculate_expected_score(team1_ratings[1], team2_avg_rating)
    player3_expected = calculate_expected_score(team2_ratings[0], team1_avg_rating)
    player4_expected = calculate_expected_score(team2_ratings[1], team1_avg_rating)
    
    # Calculate new ratings
    player1_new_rating = team1_ratings[0] + k_factor * (team1_score - player1_expected)
    player2_new_rating = team1_ratings[1] + k_factor * (team1_score - player2_expected)
    player3_new_rating = team2_ratings[0] + k_factor * (team2_score - player3_expected)
    player4_new_rating = team2_ratings[1] + k_factor * (team2_score - player4_expected)
    
    return (
        (round(player1_new_rating), round(player2_new_rating)),
        (round(player3_new_rating), round(player4_new_rating))
    )


def process_game_results(
    game_data: Dict[str, Any],
    player_ratings: Dict[str, int]
) -> Dict[str, int]:
    """Process game results and update player ratings.
    
    Args:
        game_data: Game data with player_ids and scores
        player_ratings: Dictionary mapping player_ids to current ratings
        
    Returns:
        Dictionary with updated player ratings
    """
    updated_ratings = player_ratings.copy()
    player_ids = game_data['player_ids']
    scores = game_data['scores']
    
    # Ensure all players have ratings
    for player_id in player_ids:
        if player_id not in updated_ratings:
            updated_ratings[player_id] = DEFAULT_RATING
    
    # Singles game
    if len(player_ids) == 2:
        player1_id, player2_id = player_ids
        player1_score, player2_score = scores
        player1_won = player1_score > player2_score
        
        new_ratings = update_ratings_for_singles_game(
            updated_ratings[player1_id],
            updated_ratings[player2_id],
            player1_won
        )
        
        updated_ratings[player1_id] = new_ratings[0]
        updated_ratings[player2_id] = new_ratings[1]
    
    # Doubles game
    elif len(player_ids) == 4:
        team1_ids = player_ids[:2]
        team2_ids = player_ids[2:]
        team1_score, team2_score = scores
        team1_won = team1_score > team2_score
        
        team1_ratings = (updated_ratings[team1_ids[0]], updated_ratings[team1_ids[1]])
        team2_ratings = (updated_ratings[team2_ids[0]], updated_ratings[team2_ids[1]])
        
        team1_new_ratings, team2_new_ratings = update_ratings_for_doubles_game(
            team1_ratings,
            team2_ratings,
            team1_won
        )
        
        updated_ratings[team1_ids[0]] = team1_new_ratings[0]
        updated_ratings[team1_ids[1]] = team1_new_ratings[1]
        updated_ratings[team2_ids[0]] = team2_new_ratings[0]
        updated_ratings[team2_ids[1]] = team2_new_ratings[1]
    
    return updated_ratings