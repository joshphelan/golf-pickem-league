/**
 * Format a golf score for display
 * Converts numeric score to golf notation (+5, -3, E)
 */
export function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined) {
    return '-';
  }

  if (score === 0) {
    return 'E';
  }

  if (score > 0) {
    return `+${score}`;
  }

  return score.toString();
}

/**
 * Get the appropriate CSS class for a score
 * Traditional Masters style: red for under par (good), black for over
 */
export function getScoreClass(score: number | null | undefined): string {
  if (score === null || score === undefined) {
    return 'score-even';
  }

  if (score < 0) {
    return 'score-under'; // Red - traditional Masters style for good scores
  }

  if (score > 0) {
    return 'score-over'; // Black
  }

  return 'score-even'; // Gray
}

/**
 * Get inline style for score (fallback if CSS classes not available)
 */
export function getScoreStyle(score: number | null | undefined): React.CSSProperties {
  if (score === null || score === undefined) {
    return { color: '#666666', fontWeight: 600 };
  }

  if (score < 0) {
    return { color: '#c41e3a', fontWeight: 600 }; // Masters red
  }

  if (score > 0) {
    return { color: '#1a1a1a', fontWeight: 600 }; // Black
  }

  return { color: '#666666', fontWeight: 600 }; // Gray for even
}
