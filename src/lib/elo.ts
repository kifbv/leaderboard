const K = 32;

/**
 * Computes new ELO ratings after a match between two players.
 *
 * @param winnerRating - Current ELO rating of the winner
 * @param loserRating  - Current ELO rating of the loser
 * @returns Object with new ELO ratings for winner and loser, rounded to nearest integer
 */
export function calculateElo(
  winnerRating: number,
  loserRating: number
): { newWinnerRating: number; newLoserRating: number } {
  const expectedWinner = 1 / (1 + Math.pow(10, (loserRating - winnerRating) / 400));
  const expectedLoser = 1 - expectedWinner;

  const newWinnerRating = Math.round(winnerRating + K * (1 - expectedWinner));
  const newLoserRating = Math.round(loserRating + K * (0 - expectedLoser));

  return { newWinnerRating, newLoserRating };
}
