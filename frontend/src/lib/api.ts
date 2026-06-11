const API_BASE = '/api';

export interface Match {
  id: string;
  league: string;
  home_team: string;
  away_team: string;
  match_time: string;
  odds: Record<string, number>;
  bet_type: string;
  source: string;
}

export interface BetRecommendation {
  match_id: string;
  match_summary: string;
  bet_type: string;
  selection: string;
  odds: number;
  stake: number;
  potential_return: number;
  kelly_fraction: number;
  ev_score: number;
  confidence: number;
}

export interface OptimizeResponse {
  budget: number;
  risk_level: string;
  recommendations: BetRecommendation[];
  total_stake: number;
  max_potential_return: number;
  average_ev: number;
}

export async function fetchMatches(refresh = false): Promise<Match[]> {
  const res = await fetch(`${API_BASE}/matches/?refresh=${refresh}`);
  if (!res.ok) throw new Error(`Failed to fetch matches: ${res.status}`);
  const data = await res.json();
  return data.matches || [];
}

export async function optimizeBudget(
  budget: number,
  riskLevel: string = 'moderate',
  maxMatches: number = 5
): Promise<OptimizeResponse> {
  const res = await fetch(`${API_BASE}/optimize/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      budget,
      risk_level: riskLevel,
      max_matches: maxMatches,
    }),
  });
  if (!res.ok) throw new Error(`Optimization failed: ${res.status}`);
  return res.json();
}
