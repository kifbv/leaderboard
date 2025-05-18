"""Test the ELO rating system module."""

import pytest
from src.common.elo import (
    DEFAULT_RATING,
    calculate_expected_score,
    calculate_new_rating,
    update_ratings_for_singles_game,
    update_ratings_for_doubles_game,
    process_game_results
)


def test_calculate_expected_score():
    """Test calculation of expected score based on ratings."""
    # Equal ratings should give 0.5 expectation
    assert calculate_expected_score(1200, 1200) == pytest.approx(0.5)
    
    # Higher rating should give higher expectation
    assert calculate_expected_score(1400, 1200) > 0.5
    assert calculate_expected_score(1000, 1200) < 0.5
    
    # Check specific cases
    assert calculate_expected_score(1400, 1200) == pytest.approx(0.76, abs=0.01)
    assert calculate_expected_score(1000, 1200) == pytest.approx(0.24, abs=0.01)


def test_calculate_new_rating():
    """Test calculation of new ratings after a game."""
    # Expected result, no change
    assert calculate_new_rating(1200, 1200, 0.5) == 1200
    
    # Win against equal opponent (gain points)
    assert calculate_new_rating(1200, 1200, 1.0) > 1200
    
    # Loss against equal opponent (lose points)
    assert calculate_new_rating(1200, 1200, 0.0) < 1200
    
    # Specific cases
    assert calculate_new_rating(1200, 1200, 1.0) == 1216  # Win, gain 16 points
    assert calculate_new_rating(1200, 1200, 0.0) == 1184  # Loss, lose 16 points


def test_update_ratings_for_singles_game():
    """Test updating ratings for two players in a singles game."""
    # Equal players, player1 wins
    p1_new, p2_new = update_ratings_for_singles_game(1200, 1200, True)
    assert p1_new > 1200
    assert p2_new < 1200
    assert p1_new == 1216
    assert p2_new == 1184
    
    # Equal players, player2 wins
    p1_new, p2_new = update_ratings_for_singles_game(1200, 1200, False)
    assert p1_new < 1200
    assert p2_new > 1200
    assert p1_new == 1184
    assert p2_new == 1216
    
    # Player1 is stronger, player1 wins (less points gained/lost)
    p1_new, p2_new = update_ratings_for_singles_game(1400, 1200, True)
    assert p1_new > 1400
    assert p2_new < 1200
    assert p1_new - 1400 < 16  # Gain fewer points than against equal player
    
    # Underdog wins (more points gained/lost)
    p1_new, p2_new = update_ratings_for_singles_game(1200, 1400, True)
    assert p1_new > 1200
    assert p2_new < 1400
    assert p1_new - 1200 > 16  # Gain more points as underdog


def test_update_ratings_for_doubles_game():
    """Test updating ratings for four players in a doubles game."""
    # Equal teams, team1 wins
    team1_ratings = (1200, 1200)
    team2_ratings = (1200, 1200)
    team1_new, team2_new = update_ratings_for_doubles_game(team1_ratings, team2_ratings, True)
    
    assert team1_new[0] > 1200
    assert team1_new[1] > 1200
    assert team2_new[0] < 1200
    assert team2_new[1] < 1200
    
    # Mixed team ratings
    team1_ratings = (1400, 1000)  # Average 1200
    team2_ratings = (1200, 1200)  # Average 1200
    team1_new, team2_new = update_ratings_for_doubles_game(team1_ratings, team2_ratings, True)
    
    # Both team1 players should gain points, but stronger player gains less
    assert team1_new[0] > 1400
    assert team1_new[1] > 1000
    assert team1_new[0] - 1400 < team1_new[1] - 1000  # Weaker player gains more


def test_process_game_results_singles():
    """Test processing results for a singles game."""
    # Create test data
    player_ratings = {'player1': 1200, 'player2': 1200}
    game_data = {
        'player_ids': ['player1', 'player2'],
        'scores': [21, 15]
    }
    
    # Process results (player1 won)
    updated_ratings = process_game_results(game_data, player_ratings)
    
    assert updated_ratings['player1'] > 1200
    assert updated_ratings['player2'] < 1200
    
    # Verify original dictionary wasn't modified
    assert player_ratings == {'player1': 1200, 'player2': 1200}


def test_process_game_results_doubles():
    """Test processing results for a doubles game."""
    # Create test data
    player_ratings = {
        'player1': 1200, 'player2': 1200,
        'player3': 1200, 'player4': 1200
    }
    game_data = {
        'player_ids': ['player1', 'player2', 'player3', 'player4'],
        'scores': [21, 15]
    }
    
    # Process results (team1 won)
    updated_ratings = process_game_results(game_data, player_ratings)
    
    assert updated_ratings['player1'] > 1200
    assert updated_ratings['player2'] > 1200
    assert updated_ratings['player3'] < 1200
    assert updated_ratings['player4'] < 1200
    
    # Verify original dictionary wasn't modified
    assert player_ratings == {
        'player1': 1200, 'player2': 1200,
        'player3': 1200, 'player4': 1200
    }


def test_process_game_results_new_player():
    """Test processing results when a player has no rating yet."""
    # Create test data with a missing player
    player_ratings = {'player1': 1200}
    game_data = {
        'player_ids': ['player1', 'player2'],
        'scores': [21, 15]
    }
    
    # Process results (player1 won, player2 has no rating yet)
    updated_ratings = process_game_results(game_data, player_ratings)
    
    assert updated_ratings['player1'] > 1200
    assert updated_ratings['player2'] < DEFAULT_RATING  # New player should get default rating then lose points
    assert 'player2' not in player_ratings  # Original dict unchanged