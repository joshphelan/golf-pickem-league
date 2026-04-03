'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import ProtectedRoute from '@/components/ProtectedRoute';
import { leagueAPI, tournamentAPI, configAPI, League, LeagueStanding, LeagueComment, PublicConfig } from '@/lib/api';
import { getUser } from '@/lib/auth';
import { format } from 'date-fns';
import { formatScore, getScoreStyle } from '@/lib/formatScore';
import { parseLocalDate } from '@/lib/parseDate';

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
  const [editingDeadline, setEditingDeadline] = useState(false);
  const [deadlineInput, setDeadlineInput] = useState('');
  const [savingDeadline, setSavingDeadline] = useState(false);
  const [comments, setComments] = useState<LeagueComment[]>([]);
  const [commentText, setCommentText] = useState('');
  const [postingComment, setPostingComment] = useState(false);
  const params = useParams();
  const leagueId = params.id as string;
  const user = getUser();

  useEffect(() => {
    loadLeagueData();
    configAPI.getPublicConfig().then(setConfig).catch(() => {});
    leagueAPI.getComments(leagueId).then(setComments).catch(() => {});
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

  const handleSaveDeadline = async () => {
    if (!deadlineInput) return;
    setSavingDeadline(true);
    try {
      const updated = await leagueAPI.updateLeague(leagueId, {
        draft_deadline: new Date(deadlineInput).toISOString(),
      });
      setLeague(updated);
      setEditingDeadline(false);
      setSuccessMessage('Draft deadline updated');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update deadline');
    } finally {
      setSavingDeadline(false);
    }
  };

  const handlePostComment = async () => {
    if (!commentText.trim()) return;
    setPostingComment(true);
    try {
      const comment = await leagueAPI.postComment(leagueId, commentText.trim());
      setComments((prev) => [...prev, comment]);
      setCommentText('');
    } catch {
      // silently ignore post errors
    } finally {
      setPostingComment(false);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    try {
      await leagueAPI.deleteComment(leagueId, commentId);
      setComments((prev) => prev.filter((c) => c.id !== commentId));
    } catch {
      // silently ignore delete errors
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
      <div className="min-h-screen bg-[var(--cream)]">
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
            <div className="bg-gradient-to-br from-[var(--masters-green)] to-[var(--masters-green-dark)] border-b-[3px] border-[var(--masters-gold)]">
              <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-3 mb-3">
                      {tournamentStatus === 'active' && (
                        <span className="text-xs uppercase tracking-wider font-medium px-3 py-1 rounded-full bg-[var(--masters-gold)] text-[var(--charcoal)]">
                          Live - Round {currentRound}
                        </span>
                      )}
                      {tournamentStatus === 'upcoming' && (
                        <span className="text-xs uppercase tracking-wider font-medium px-3 py-1 rounded-full bg-white/20 text-white">
                          Upcoming
                        </span>
                      )}
                    </div>
                    <h1 className="text-2xl text-white mb-1 font-display">
                      {league.name}
                    </h1>
                    <p className="text-white/70 text-sm">
                      {league.tournament?.name}
                      {league.tournament?.start_date && (
                        <span className="ml-2">
                          {format(parseLocalDate(league.tournament.start_date), 'MMM d')} -{' '}
                          {league.tournament?.end_date &&
                            format(parseLocalDate(league.tournament.end_date), 'd, yyyy')}
                        </span>
                      )}
                    </p>
                  </div>
                  {userTeam && (
                    <Link
                      href={`/teams/${userTeam.team_id}`}
                      className="px-5 py-2 text-sm font-medium rounded-lg bg-[var(--masters-gold)] text-[var(--charcoal)] transition-all hover:brightness-110 hover:shadow-md"
                    >
                      My Team
                    </Link>
                  )}
                </div>
              </div>
            </div>

            <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
              <ErrorMessage message={error} />
              {successMessage && (
                <div className="mb-4 px-4 py-2.5 text-sm bg-green-50 text-green-700 rounded-xl">
                  {successMessage}
                </div>
              )}

              {/* Info Bar */}
              <div className="flex flex-wrap items-center gap-6 mb-6 pb-5 border-b border-[#e5e2d3]">
                <div>
                  <p className="text-xs uppercase tracking-wider text-gray-400">
                    Draft Deadline
                  </p>
                  {editingDeadline ? (
                    <div className="flex items-center gap-2 mt-1">
                      <input
                        type="datetime-local"
                        value={deadlineInput}
                        onChange={(e) => setDeadlineInput(e.target.value)}
                        min={new Date().toISOString().slice(0, 16)}
                        className="text-sm border border-[#e5e2d3] rounded-lg px-2 py-1"
                      />
                      <button onClick={handleSaveDeadline} disabled={savingDeadline} className="text-xs px-2 py-1 rounded bg-[var(--masters-green)] text-white disabled:opacity-50">
                        {savingDeadline ? '...' : 'Save'}
                      </button>
                      <button onClick={() => setEditingDeadline(false)} className="text-xs px-2 py-1 rounded bg-gray-100 text-gray-600">
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <p className="text-sm text-[var(--charcoal)]">
                        {format(new Date(league.draft_deadline), 'MMM d, h:mm a')}
                      </p>
                      {isLeagueOwner && (
                        <button
                          onClick={() => {
                            const d = new Date(league.draft_deadline);
                            setDeadlineInput(format(d, "yyyy-MM-dd'T'HH:mm"));
                            setEditingDeadline(true);
                          }}
                          className="text-gray-400 hover:text-[var(--masters-green)] transition-colors text-xs"
                          aria-label="Edit draft deadline"
                        >
                          ✏️
                        </button>
                      )}
                    </div>
                  )}
                </div>

                <div>
                  <p className="text-xs uppercase tracking-wider text-gray-400">
                    Invite Code
                  </p>
                  <button
                    onClick={copyInviteCode}
                    className="flex items-center gap-2 text-sm font-mono tracking-wider text-[var(--masters-green)] transition-colors"
                  >
                    {league.invite_code}
                    <span
                      className="text-xs px-2 py-0.5 rounded-full transition-colors"
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
                      className="px-4 py-1.5 text-sm font-medium disabled:opacity-50 rounded-lg bg-[var(--masters-green)] text-white transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-sm"
                    >
                      {syncing ? 'Syncing...' : 'Sync Scores'}
                    </button>
                    {tournamentStatus === 'upcoming' && (
                      <button
                        onClick={handleRefreshPlayers}
                        disabled={refreshing}
                        className="px-4 py-1.5 text-sm disabled:opacity-50 rounded-lg bg-[var(--cream-dark)] text-[var(--charcoal)] transition-all hover:bg-[#ebe8da]"
                      >
                        {refreshing ? 'Refreshing...' : 'Refresh Field'}
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Update Notice */}
              {tournamentStatus === 'active' && (
                <div className="mb-6 px-4 py-2.5 text-xs bg-[var(--cream-dark)] text-gray-500 rounded-lg">
                  Scores update every {syncInterval} minutes during active tournament hours ({formatHour(hoursStart)} - {formatHour(hoursEnd)} local time)
                  {standingsData?.last_score_sync && (
                    <span className="ml-3 text-gray-400">
                      Last refresh: {format(new Date(standingsData.last_score_sync), "EEE MMMM d 'at' h:mm a")}
                    </span>
                  )}
                </div>
              )}

              {/* Leaderboard */}
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-display text-[var(--charcoal)]">
                  Leaderboard
                </h2>
                {currentRound > 0 && (
                  <span className="text-sm text-gray-400">
                    Through Round {currentRound}
                  </span>
                )}
              </div>

              {standings.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-xl text-gray-500">
                  No teams have drafted players yet.
                </div>
              ) : (
                <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                  {/* Header */}
                  <div
                    className="standings-grid grid gap-4 px-4 sm:px-5 py-3 text-xs uppercase tracking-wider bg-[var(--masters-green)] text-white border-b-2 border-[var(--masters-gold)]"
                    style={{ gridTemplateColumns: '3rem 1fr auto 5rem' }}
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
                      className="standings-grid grid gap-4 px-4 sm:px-5 py-4 sm:py-5 items-center transition-colors hover:bg-[var(--cream-dark)]"
                      style={{
                        gridTemplateColumns: '3rem 1fr auto 5rem',
                        borderBottom: idx < standings.length - 1 ? '1px solid #f0ede3' : 'none',
                      }}
                    >
                      <span className="font-semibold text-[var(--charcoal)]">
                        {standing.rank || '-'}
                      </span>
                      <div className="min-w-0">
                        <Link
                          href={`/teams/${standing.team_id}`}
                          className="font-medium hover:underline truncate block text-[var(--masters-green)]"
                        >
                          {standing.team_name}
                        </Link>
                        <div className="flex flex-wrap gap-x-3 mt-1">
                          {standing.players.map((player) => (
                            <span
                              key={player.player_id}
                              className="text-sm text-gray-400"
                            >
                              {player.name.split(' ').pop()}{' '}
                              <span style={getScoreStyle(player.score)}>
                                {formatScore(player.score)}
                              </span>
                            </span>
                          ))}
                        </div>
                      </div>
                      <span className="hide-mobile text-sm text-gray-500">
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

              {/* League Chat */}
              <div className="mt-10">
                <h2 className="text-lg font-display text-[var(--charcoal)] mb-4">League Chat</h2>
                <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                  {comments.length === 0 ? (
                    <p className="px-5 py-6 text-sm text-gray-400">No messages yet. Be the first to post!</p>
                  ) : (
                    <div className="divide-y divide-[#f0ede3]">
                      {comments.map((c) => (
                        <div key={c.id} className="px-5 py-3 flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <span className="text-xs font-medium text-[var(--masters-green)] mr-2">{c.username}</span>
                            <span className="text-xs text-gray-400">
                              {format(new Date(c.created_at), "MMM d 'at' h:mm a")}
                            </span>
                            <p className="text-sm text-[var(--charcoal)] mt-0.5 break-words">{c.content}</p>
                          </div>
                          {(user?.id === c.user_id || isLeagueOwner) && (
                            <button
                              onClick={() => handleDeleteComment(c.id)}
                              className="text-xs text-gray-300 hover:text-red-400 transition-colors flex-shrink-0 mt-0.5"
                              aria-label="Delete comment"
                            >
                              ✕
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="px-5 py-3 border-t border-[#f0ede3] flex gap-2">
                    <input
                      type="text"
                      value={commentText}
                      onChange={(e) => setCommentText(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handlePostComment(); } }}
                      placeholder="Add a message..."
                      maxLength={1000}
                      className="flex-1 px-3 py-2 text-sm border border-[#e5e2d3] rounded-lg transition-all"
                    />
                    <button
                      onClick={handlePostComment}
                      disabled={postingComment || !commentText.trim()}
                      className="px-4 py-2 text-sm font-medium disabled:opacity-40 rounded-lg bg-[var(--masters-green)] text-white transition-all hover:bg-[var(--masters-green-dark)]"
                    >
                      Post
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </ProtectedRoute>
  );
}
