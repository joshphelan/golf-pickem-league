'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import ProtectedRoute from '@/components/ProtectedRoute';
import { leagueAPI, tournamentAPI, configAPI, League, LeagueStanding, PublicConfig } from '@/lib/api';
import { getUser } from '@/lib/auth';
import { format } from 'date-fns';
import { formatScore, getScoreStyle } from '@/lib/formatScore';

interface StandingsResponse {
  league_id: string;
  league_name: string;
  current_round: number;
  last_score_sync: string | null;
  tournament: {
    id: string;
    name: string;
    status: string;
    start_date: string;
    end_date: string;
  } | null;
  standings: LeagueStanding[];
}

export default function LeagueDetailsPage() {
  const [league, setLeague] = useState<League | null>(null);
  const [standingsData, setStandingsData] = useState<StandingsResponse | null>(null);
  const [config, setConfig] = useState<PublicConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [copied, setCopied] = useState(false);
  const params = useParams();
  const leagueId = params.id as string;
  const user = getUser();

  useEffect(() => {
    loadLeagueData();
    configAPI.getPublicConfig().then(setConfig).catch(() => {});
  }, []);

  const loadLeagueData = async () => {
    try {
      const [leagueData, standingsRes] = await Promise.all([
        leagueAPI.getLeague(leagueId),
        leagueAPI.getLeagueStandings(leagueId),
      ]);
      setLeague(leagueData);
      setStandingsData(standingsRes);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load league data');
    } finally {
      setLoading(false);
    }
  };

  const handleSyncScores = async () => {
    if (!league?.tournament_id) return;
    setError('');
    setSuccessMessage('');
    setSyncing(true);

    try {
      await tournamentAPI.syncScores(league.tournament_id);
      setSuccessMessage('Scores synced');
      const standingsRes = await leagueAPI.getLeagueStandings(leagueId);
      setStandingsData(standingsRes);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sync scores');
    } finally {
      setSyncing(false);
    }
  };

  const handleRefreshPlayers = async () => {
    if (!league?.tournament_id) return;
    setError('');
    setSuccessMessage('');
    setRefreshing(true);

    try {
      const result = await tournamentAPI.refreshPlayers(league.tournament_id);
      setSuccessMessage(result.message);
      await loadLeagueData();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to refresh players');
    } finally {
      setRefreshing(false);
    }
  };

  const copyInviteCode = async () => {
    if (league) {
      await navigator.clipboard.writeText(league.invite_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const isLeagueOwner = user?.id === league?.admin_id || user?.is_owner;
  const userTeam = standingsData?.standings.find((s) => s.owner_name === user?.username);
  const standings = standingsData?.standings || [];
  const currentRound = standingsData?.current_round || 0;
  const tournamentStatus = standingsData?.tournament?.status || league?.tournament?.status;

  const syncInterval = config?.sync_interval_minutes ?? 15;
  const hoursStart = config?.playing_hours_start ?? 7;
  const hoursEnd = config?.playing_hours_end ?? 21;
  const formatHour = (h: number) => {
    const ampm = h >= 12 ? 'PM' : 'AM';
    const hour12 = h % 12 || 12;
    return `${hour12} ${ampm}`;
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen" style={{ background: '#fffef7' }}>
        <Navbar />

        {loading ? (
          <LoadingSpinner />
        ) : !league ? (
          <div className="max-w-4xl mx-auto px-6 py-10">
            <ErrorMessage message="League not found" />
          </div>
        ) : (
          <>
            {/* Tournament Header */}
            <div
              style={{
                background: 'linear-gradient(135deg, #006747 0%, #004d35 100%)',
                borderBottom: '3px solid #c9a227',
              }}
            >
              <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      {tournamentStatus === 'active' && (
                        <span
                          className="text-xs uppercase tracking-wider px-2 py-0.5"
                          style={{ background: '#c9a227', color: '#1a1a1a' }}
                        >
                          Live - Round {currentRound}
                        </span>
                      )}
                      {tournamentStatus === 'upcoming' && (
                        <span
                          className="text-xs uppercase tracking-wider px-2 py-0.5"
                          style={{ background: 'rgba(255,255,255,0.2)', color: 'white' }}
                        >
                          Upcoming
                        </span>
                      )}
                    </div>
                    <h1
                      className="text-2xl text-white mb-1"
                      style={{ fontFamily: 'Georgia, serif' }}
                    >
                      {league.name}
                    </h1>
                    <p className="text-white/70 text-sm">
                      {league.tournament?.name}
                      {league.tournament?.start_date && (
                        <span className="ml-2">
                          {format(new Date(league.tournament.start_date), 'MMM d')} -{' '}
                          {league.tournament?.end_date &&
                            format(new Date(league.tournament.end_date), 'd, yyyy')}
                        </span>
                      )}
                    </p>
                  </div>
                  {userTeam && (
                    <Link
                      href={`/teams/${userTeam.team_id}`}
                      className="px-5 py-2 text-sm font-medium"
                      style={{ background: '#c9a227', color: '#1a1a1a' }}
                    >
                      My Team
                    </Link>
                  )}
                </div>
              </div>
            </div>

            <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 sm:py-6">
              <ErrorMessage message={error} />
              {successMessage && (
                <div
                  className="mb-4 px-4 py-2 text-sm"
                  style={{ background: '#e8f5e9', color: '#2e7d32' }}
                >
                  {successMessage}
                </div>
              )}

              {/* Info Bar */}
              <div
                className="flex flex-wrap items-center gap-6 mb-6 pb-5"
                style={{ borderBottom: '1px solid #e5e2d3' }}
              >
                <div>
                  <p className="text-xs uppercase tracking-wider" style={{ color: '#888' }}>
                    Draft Deadline
                  </p>
                  <p className="text-sm" style={{ color: '#1a1a1a' }}>
                    {format(new Date(league.draft_deadline), 'MMM d, h:mm a')}
                  </p>
                </div>

                <div>
                  <p className="text-xs uppercase tracking-wider" style={{ color: '#888' }}>
                    Invite Code
                  </p>
                  <button
                    onClick={copyInviteCode}
                    className="flex items-center gap-2 text-sm font-mono tracking-wider transition-colors"
                    style={{ color: '#006747' }}
                  >
                    {league.invite_code}
                    <span
                      className="text-xs px-1.5 py-0.5"
                      style={{
                        background: copied ? '#e8f5e9' : '#f5f5f5',
                        color: copied ? '#2e7d32' : '#888',
                      }}
                    >
                      {copied ? 'Copied!' : 'Copy'}
                    </span>
                  </button>
                </div>

                <div className="flex-1"></div>

                {isLeagueOwner && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleSyncScores}
                      disabled={syncing}
                      className="px-4 py-1.5 text-sm font-medium disabled:opacity-50 transition-opacity"
                      style={{ background: '#006747', color: 'white' }}
                    >
                      {syncing ? 'Syncing...' : 'Sync Scores'}
                    </button>
                    {tournamentStatus === 'upcoming' && (
                      <button
                        onClick={handleRefreshPlayers}
                        disabled={refreshing}
                        className="px-4 py-1.5 text-sm disabled:opacity-50"
                        style={{ background: '#e5e2d3', color: '#1a1a1a' }}
                      >
                        {refreshing ? 'Refreshing...' : 'Refresh Field'}
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Update Notice */}
              {tournamentStatus === 'active' && (
                <div
                  className="mb-6 px-4 py-2 text-xs"
                  style={{ background: '#f5f3e7', color: '#666' }}
                >
                  Scores update every {syncInterval} minutes during active tournament hours ({formatHour(hoursStart)} - {formatHour(hoursEnd)} local time)
                  {standingsData?.last_score_sync && (
                    <span className="ml-3" style={{ color: '#888' }}>
                      Last refresh: {format(new Date(standingsData.last_score_sync), 'h:mm a')}
                    </span>
                  )}
                </div>
              )}

              {/* Leaderboard */}
              <div className="mb-4 flex items-center justify-between">
                <h2
                  className="text-lg"
                  style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}
                >
                  Leaderboard
                </h2>
                {currentRound > 0 && (
                  <span className="text-sm" style={{ color: '#888' }}>
                    Through Round {currentRound}
                  </span>
                )}
              </div>

              {standings.length === 0 ? (
                <div
                  className="text-center py-12"
                  style={{ background: 'white', color: '#666' }}
                >
                  No teams have drafted players yet.
                </div>
              ) : (
                <div style={{ background: 'white' }}>
                  {/* Header */}
                  <div
                    className="standings-grid grid gap-4 px-3 sm:px-4 py-3 text-xs uppercase tracking-wider"
                    style={{
                      gridTemplateColumns: '3rem 1fr auto 5rem',
                      background: '#006747',
                      color: 'white',
                      borderBottom: '2px solid #c9a227',
                    }}
                  >
                    <span>Pos</span>
                    <span>Team</span>
                    <span className="hide-mobile">Owner</span>
                    <span className="text-right">Score</span>
                  </div>

                  {/* Rows */}
                  {standings.map((standing, idx) => (
                    <div
                      key={standing.team_id}
                      className="standings-grid grid gap-4 px-3 sm:px-4 py-3 sm:py-4 items-center transition-colors"
                      style={{
                        gridTemplateColumns: '3rem 1fr auto 5rem',
                        borderBottom: '1px solid #f0f0f0',
                        background: idx % 2 === 0 ? 'white' : '#fafafa',
                      }}
                    >
                      <span className="font-semibold" style={{ color: '#1a1a1a' }}>
                        {standing.rank || '-'}
                      </span>
                      <div className="min-w-0">
                        <Link
                          href={`/teams/${standing.team_id}`}
                          className="font-medium hover:underline truncate block"
                          style={{ color: '#006747' }}
                        >
                          {standing.team_name}
                        </Link>
                        <div className="flex flex-wrap gap-x-3 mt-1">
                          {standing.players.map((player) => (
                            <span
                              key={player.player_id}
                              className="text-sm"
                              style={{ color: '#888' }}
                            >
                              {player.name.split(' ').pop()}{' '}
                              <span style={getScoreStyle(player.score)}>
                                {formatScore(player.score)}
                              </span>
                            </span>
                          ))}
                        </div>
                      </div>
                      <span className="hide-mobile text-sm" style={{ color: '#666' }}>
                        {standing.owner_name}
                      </span>
                      <span
                        className="text-right text-lg"
                        style={getScoreStyle(standing.total_score)}
                      >
                        {formatScore(standing.total_score)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </ProtectedRoute>
  );
}
