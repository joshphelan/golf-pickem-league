import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Type definitions
export interface User {
  id: string;
  email: string;
  username: string;
  is_approved: boolean;
  is_league_admin: boolean;
  is_owner: boolean;
  is_primary_owner: boolean;
  created_at: string;
}

export interface Tournament {
  id: string;
  tourn_id: string;
  name: string;
  year: number;
  start_date: string;
  end_date: string;
  venue?: string;
  purse?: string;
  status: string;
  timezone: string;
  created_at: string;
}

export interface League {
  id: string;
  name: string;
  tournament_id: string;
  admin_id: string;
  tournament?: Tournament;
  draft_deadline: string;
  team_size: number;
  invite_code: string;
  created_at: string;
}

export interface Player {
  id: string;
  player_id: string;
  first_name: string;
  last_name: string;
  is_amateur: boolean;
}

export interface TeamPlayer {
  id: string;
  team_id: string;
  player_id: string;
  drafted_at: string;
  player: {
    id: string;
    player_id: string;
    first_name: string;
    last_name: string;
    full_name: string;
    country?: string;
  };
  scores?: {
    round_1?: number | null;
    round_2?: number | null;
    round_3?: number | null;
    round_4?: number | null;
    total_score?: number | null;
  };
}

export interface Team {
  id: string;
  name: string;
  league_id: string;
  user_id: string;
  owner?: User;
  created_at: string;
  players?: TeamPlayer[];
  total_score?: number | null;
}

export interface LeagueStanding {
  rank: number;
  team_id: string;
  team_name: string;
  owner_name: string;
  total_score: number | null;
  players: {
    player_id: string;
    name: string;
    score: number | null;
  }[];
}

// Auth API
export const authAPI = {
  signup: async (email: string, username: string, password: string) => {
    const response = await api.post('/auth/signup', { email, username, password });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export interface LiveTournament {
  tournament: {
    id: string;
    name: string;
    status: string;
    start_date: string;
    end_date: string;
  } | null;
  current_round: number;
  leaderboard: {
    position: number;
    player_name: string;
    total_score: number;
    made_cut: boolean;
  }[];
}

// Tournament API
export const tournamentAPI = {
  getTournaments: async (): Promise<Tournament[]> => {
    const response = await api.get('/tournaments');
    return response.data;
  },

  getLiveTournament: async (): Promise<LiveTournament> => {
    const response = await api.get('/tournaments/active/live');
    return response.data;
  },

  getTournament: async (tournamentId: string): Promise<Tournament> => {
    const response = await api.get(`/tournaments/${tournamentId}`);
    return response.data;
  },

  importTournament: async (tournId: string, year: number): Promise<Tournament> => {
    const response = await api.post('/tournaments/import', { tourn_id: tournId, year });
    return response.data;
  },

  syncScores: async (tournamentId: string): Promise<Tournament> => {
    const response = await api.post(`/tournaments/${tournamentId}/sync-scores`);
    return response.data;
  },

  getAvailablePlayers: async (tournamentId: string, leagueId: string): Promise<Player[]> => {
    const response = await api.get(`/tournaments/${tournamentId}/available-players`, {
      params: { league_id: leagueId },
    });
    return response.data;
  },

  getSchedule: async (year?: number): Promise<Tournament[]> => {
    const response = await api.get('/tournaments/schedule', {
      params: year ? { year } : {},
    });
    return response.data;
  },

  refreshPlayers: async (tournamentId: string): Promise<{ message: string; players_added: number }> => {
    const response = await api.post(`/tournaments/${tournamentId}/refresh-players`);
    return response.data;
  },
};

// League API
export const leagueAPI = {
  createLeague: async (data: {
    name: string;
    tournament_id: string;
    draft_deadline: string;
    team_size: number;
  }): Promise<League> => {
    const response = await api.post('/leagues', data);
    return response.data;
  },

  getLeague: async (leagueId: string): Promise<League> => {
    const response = await api.get(`/leagues/${leagueId}`);
    return response.data;
  },

  getUserLeagues: async (): Promise<League[]> => {
    const response = await api.get('/leagues/my-leagues');
    return response.data;
  },

  joinLeague: async (inviteCode: string): Promise<{ league: League; team: Team }> => {
    const response = await api.post(`/leagues/join/${inviteCode}`);
    return response.data;
  },

  getLeagueStandings: async (leagueId: string, round?: number) => {
    const response = await api.get(`/leagues/${leagueId}/standings`, {
      params: round ? { round: round } : {},
    });
    return response.data;
  },
};

// Team API
export const teamAPI = {
  getTeam: async (teamId: string, round?: number): Promise<Team> => {
    const response = await api.get(`/teams/${teamId}`, {
      params: round ? { round: round } : {},
    });
    return response.data;
  },

  draftPlayer: async (teamId: string, playerId: string): Promise<Team> => {
    const response = await api.post(`/teams/${teamId}/players`, { player_id: playerId });
    return response.data;
  },

  undraftPlayer: async (teamId: string, playerId: string): Promise<Team> => {
    const response = await api.delete(`/teams/${teamId}/players/${playerId}`);
    return response.data;
  },
};

// Config API
export interface PublicConfig {
  sync_interval_minutes: number;
  playing_hours_start: number;
  playing_hours_end: number;
}

export const configAPI = {
  getPublicConfig: async (): Promise<PublicConfig> => {
    const response = await api.get('/config/public');
    return response.data;
  },
};

export default api;

