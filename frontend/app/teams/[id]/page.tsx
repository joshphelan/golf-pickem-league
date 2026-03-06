'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import ProtectedRoute from '@/components/ProtectedRoute';
import { teamAPI, tournamentAPI, leagueAPI, Team, Player } from '@/lib/api';
import { getUser } from '@/lib/auth';
import { format } from 'date-fns';
import { formatScore, getScoreStyle } from '@/lib/formatScore';

export default function TeamDetailsPage() {
  const [team, setTeam] = useState<Team | null>(null);
  const [availablePlayers, setAvailablePlayers] = useState<Player[]>([]);
  const [filteredPlayers, setFilteredPlayers] = useState<Player[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [drafting, setDrafting] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [showDraftModal, setShowDraftModal] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const params = useParams();
  const teamId = params.id as string;

  useEffect(() => {
    setUser(getUser());
    loadTeamData();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const filtered = availablePlayers.filter((player) => {
        const fullName = `${player.first_name} ${player.last_name}`.toLowerCase();
        return fullName.includes(searchTerm.toLowerCase());
      });
      setFilteredPlayers(filtered);
    } else {
      setFilteredPlayers(availablePlayers);
    }
  }, [searchTerm, availablePlayers]);

  const loadTeamData = async () => {
    try {
      const teamData = await teamAPI.getTeam(teamId);
      setTeam(teamData);
      setLastUpdated(new Date());
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load team data');
    } finally {
      setLoading(false);
    }
  };

  const loadAvailablePlayers = async () => {
    if (!team?.league_id) return;

    try {
      const leagueData = await leagueAPI.getLeague(team.league_id);
      if (!leagueData.tournament_id) {
        setError('League has no associated tournament');
        return;
      }

      const players = await tournamentAPI.getAvailablePlayers(
        leagueData.tournament_id,
        team.league_id
      );
      setAvailablePlayers(players);
      setFilteredPlayers(players);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load available players');
    }
  };

  const handleDraftPlayer = async (playerId: string) => {
    setError('');
    setSuccessMessage('');
    setDrafting(true);

    try {
      await teamAPI.draftPlayer(teamId, playerId);
      const updatedTeam = await teamAPI.getTeam(teamId);
      setTeam(updatedTeam);
      setLastUpdated(new Date());
      await loadAvailablePlayers();

      const newCount = updatedTeam.players?.length || 0;
      if (newCount >= maxPlayers) {
        setShowDraftModal(false);
        setSuccessMessage('Roster complete');
      } else {
        setSuccessMessage('Player drafted');
      }
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to draft player');
    } finally {
      setDrafting(false);
    }
  };

  const handleUndraftPlayer = async (playerId: string) => {
    setError('');
    setSuccessMessage('');

    try {
      await teamAPI.undraftPlayer(teamId, playerId);
      setSuccessMessage('Player removed');
      await loadTeamData();
      await loadAvailablePlayers();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to remove player');
    }
  };

  const openDraftModal = async () => {
    setShowDraftModal(true);
    if (availablePlayers.length === 0) {
      await loadAvailablePlayers();
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-[var(--cream)]">
          <Navbar />
          <LoadingSpinner />
        </div>
      </ProtectedRoute>
    );
  }

  if (!team) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-[var(--cream)]">
          <Navbar />
          <div className="max-w-4xl mx-auto px-6 py-10">
            <ErrorMessage message="Team not found" />
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  const isOwner = user?.id === team.user_id;
  const draftedCount = team.players?.length || 0;
  const maxPlayers = 4;
  const canDraft = isOwner && draftedCount < maxPlayers;

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[var(--cream)]">
        <Navbar />

        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          {/* Header */}
          <div className="mb-6">
            <Link
              href={`/leagues/${team.league_id}`}
              className="text-sm text-[var(--masters-green)] hover:underline inline-flex items-center gap-1"
            >
              <span>&larr;</span> Back to League
            </Link>
            <h1 className="text-2xl mt-2 font-display text-[var(--charcoal)]">
              {team.name}
            </h1>
            {lastUpdated && (
              <p className="text-xs mt-1 text-gray-400">
                Updated {format(lastUpdated, 'h:mm a')}
              </p>
            )}
          </div>

          <ErrorMessage message={error} />
          {successMessage && (
            <div className="mb-4 px-4 py-2.5 text-sm bg-green-50 text-green-700 rounded-xl">
              {successMessage}
            </div>
          )}

          {/* Team Score Card */}
          <div className="mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-br from-[var(--masters-green)] to-[var(--masters-green-dark)] p-6 rounded-xl shadow-md">
            <div>
              <p className="text-xs uppercase tracking-widest mb-1 text-white/70">
                Total Score
              </p>
              <p className="text-4xl font-display text-white">
                {formatScore(team.total_score)}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs uppercase tracking-widest mb-1 text-white/70">
                Roster
              </p>
              <p className="text-lg text-white">
                {draftedCount} / {maxPlayers}
              </p>
              {canDraft && (
                <button
                  onClick={openDraftModal}
                  className="mt-2 px-4 py-1.5 text-sm font-medium rounded-lg bg-[var(--masters-gold)] text-[var(--charcoal)] transition-all hover:brightness-110 hover:shadow-md"
                >
                  Draft Player
                </button>
              )}
            </div>
          </div>

          {/* Roster Table */}
          {draftedCount === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl text-gray-500">
              No players drafted yet. Click &quot;Draft Player&quot; to build your team.
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              {/* Header */}
              <div
                className={`roster-grid${isOwner ? ' has-actions' : ''} grid gap-2 px-4 sm:px-5 py-3 text-xs uppercase tracking-wider bg-[var(--masters-green)] text-white border-b-2 border-[var(--masters-gold)]`}
                style={{
                  gridTemplateColumns: '1fr repeat(4, 4rem) 5rem' + (isOwner ? ' 4rem' : ''),
                }}
              >
                <span>Player</span>
                <span className="hide-mobile text-center">R1</span>
                <span className="hide-mobile text-center">R2</span>
                <span className="hide-mobile text-center">R3</span>
                <span className="hide-mobile text-center">R4</span>
                <span className="text-center">Total</span>
                {isOwner && <span></span>}
              </div>

              {/* Rows */}
              {team.players?.map((teamPlayer, idx) => (
                <div
                  key={teamPlayer.id}
                  className={`roster-grid${isOwner ? ' has-actions' : ''} grid gap-2 px-4 sm:px-5 py-4 sm:py-5 items-center transition-colors hover:bg-[var(--cream-dark)]`}
                  style={{
                    gridTemplateColumns: '1fr repeat(4, 4rem) 5rem' + (isOwner ? ' 4rem' : ''),
                    borderBottom: idx < (team.players?.length || 0) - 1 ? '1px solid #f0ede3' : 'none',
                  }}
                >
                  <span className="font-medium truncate text-[var(--charcoal)]">
                    {teamPlayer.player.full_name}
                  </span>
                  <span className="hide-mobile text-center" style={getScoreStyle(teamPlayer.scores?.round_1)}>
                    {formatScore(teamPlayer.scores?.round_1)}
                  </span>
                  <span className="hide-mobile text-center" style={getScoreStyle(teamPlayer.scores?.round_2)}>
                    {formatScore(teamPlayer.scores?.round_2)}
                  </span>
                  <span className="hide-mobile text-center" style={getScoreStyle(teamPlayer.scores?.round_3)}>
                    {formatScore(teamPlayer.scores?.round_3)}
                  </span>
                  <span className="hide-mobile text-center" style={getScoreStyle(teamPlayer.scores?.round_4)}>
                    {formatScore(teamPlayer.scores?.round_4)}
                  </span>
                  <span
                    className="text-center font-semibold"
                    style={getScoreStyle(teamPlayer.scores?.total_score)}
                  >
                    {formatScore(teamPlayer.scores?.total_score)}
                  </span>
                  {isOwner && (
                    <button
                      onClick={() => handleUndraftPlayer(teamPlayer.player.id)}
                      className="text-sm text-right text-red-500 hover:text-red-700 transition-colors"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Draft Modal */}
        {showDraftModal && (
          <div className="fixed inset-0 flex items-end sm:items-center justify-center p-0 sm:p-4 z-50 bg-black/50 backdrop-blur-sm">
            <div className="w-full sm:max-w-lg sm:max-h-[80vh] max-h-[90vh] overflow-hidden bg-[var(--cream)] rounded-t-2xl sm:rounded-2xl shadow-2xl">
              <div className="px-5 py-4 flex justify-between items-center bg-[var(--masters-green)] border-b-2 border-[var(--masters-gold)] sm:rounded-t-2xl">
                <div>
                  <h2 className="text-lg text-white font-display">
                    Draft Player
                  </h2>
                  <p className="text-sm text-white/70">
                    {maxPlayers - draftedCount} slot{maxPlayers - draftedCount !== 1 ? 's' : ''} remaining
                  </p>
                </div>
                <button
                  onClick={() => setShowDraftModal(false)}
                  className="text-white/70 hover:text-white text-2xl leading-none transition-colors w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10"
                >
                  &times;
                </button>
              </div>

              <div className="p-5">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search players..."
                  className="w-full px-4 py-2.5 border border-[#e5e2d3] rounded-lg text-sm mb-4"
                />

                <div className="overflow-y-auto max-h-[50vh]">
                  {filteredPlayers.length === 0 ? (
                    <p className="text-center py-8 text-gray-400">
                      No available players found.
                    </p>
                  ) : (
                    <div>
                      {filteredPlayers.map((player, index) => (
                        <div
                          key={player.player_id}
                          className="flex justify-between items-center py-3 px-2 rounded-lg hover:bg-white transition-colors"
                          style={{
                            borderBottom:
                              index < filteredPlayers.length - 1 ? '1px solid #f0ede3' : 'none',
                          }}
                        >
                          <div>
                            <p className="font-medium text-[var(--charcoal)]">
                              {player.first_name} {player.last_name}
                            </p>
                            {player.is_amateur && (
                              <span className="text-xs text-gray-400">
                                Amateur
                              </span>
                            )}
                          </div>
                          <button
                            onClick={() => handleDraftPlayer(player.id)}
                            disabled={drafting}
                            className="px-4 py-1.5 text-sm font-medium disabled:opacity-50 rounded-lg bg-[var(--masters-green)] text-white transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-sm"
                          >
                            {drafting ? '...' : 'Draft'}
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}
