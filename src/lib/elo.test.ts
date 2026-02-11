import { describe, it, expect } from "vitest";
import { calculateElo } from "./elo";

describe("calculateElo", () => {
  it("equal ratings: winner gains 16, loser loses 16", () => {
    const { newWinnerRating, newLoserRating } = calculateElo(1000, 1000);
    expect(newWinnerRating).toBe(1016);
    expect(newLoserRating).toBe(984);
  });

  it("underdog wins (1000 beats 1200): underdog gains 24, favorite loses 24", () => {
    const { newWinnerRating, newLoserRating } = calculateElo(1000, 1200);
    expect(newWinnerRating).toBe(1024);
    expect(newLoserRating).toBe(1176);
  });

  it("favorite wins (1200 beats 1000): favorite gains 8, underdog loses 8", () => {
    const { newWinnerRating, newLoserRating } = calculateElo(1200, 1000);
    expect(newWinnerRating).toBe(1208);
    expect(newLoserRating).toBe(992);
  });
});
