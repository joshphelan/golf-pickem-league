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
        <div className="min-h-screen" style={{ background: '#fffef7' }}>
          <Navbar />
          <LoadingSpinner />
        </div>
      </ProtectedRoute>
    );
  }

  if (!team) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen" style={{ background: '#fffef7' }}>
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
      <div className="min-h-screen" style={{ background: '#fffef7' }}>
        <Navbar />

        <div className="max-w-4xl mx-auto px-6 py-8">
          {/* Header */}
          <div className="mb-6">
            <Link
              href={`/leagues/${team.league_id}`}
              className="text-sm hover:underline inline-flex items-center gap-1"
              style={{ color: '#006747' }}
            >
              <span>←</span> Back to League
            </Link>
            <h1
              className="text-2xl mt-2"
              style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}
            >
              {team.name}
            </h1>
            {lastUpdated && (
              <p className="text-xs mt-1" style={{ color: '#888' }}>
                Updated {format(lastUpdated, 'h:mm a')}
              </p>
            )}
          </div>

          <ErrorMessage message={error} />
          {successMessage && (
            <div
              className="mb-4 px-4 py-2 text-sm"
              style={{ background: '#e8f5e9', color: '#2e7d32' }}
            >
              {successMessage}
            </div>
          )}

          {/* Team Score Card */}
          <div
            className="mb-8 flex items-center justify-between"
            style={{
              background: 'linear-gradient(135deg, #006747 0%, #004d35 100%)',
              padding: '1.5rem',
            }}
          >
            <div>
              <p
                className="text-xs uppercase tracking-widest mb-1"
                style={{ color: 'rgba(255,255,255,0.7)' }}
              >
                Total Score
              </p>
              <p
                className="text-4xl"
                style={{ fontFamily: 'Georgia, serif', color: 'white' }}
              >
                {formatScore(team.total_score)}
              </p>
            </div>
            <div className="text-right">
              <p
                className="text-xs uppercase tracking-widest mb-1"
                style={{ color: 'rgba(255,255,255,0.7)' }}
              >
                Roster
              </p>
              <p className="text-lg" style={{ color: 'white' }}>
                {draftedCount} / {maxPlayers}
              </p>
              {canDraft && (
                <button
                  onClick={openDraftModal}
                  className="mt-2 px-4 py-1.5 text-sm font-medium"
                  style={{ background: '#c9a227', color: '#1a1a1a' }}
                >
                  Draft Player
                </button>
              )}
            </div>
          </div>

          {/* Roster Table */}
          {draftedCount === 0 ? (
            <div
              className="text-center py-12"
              style={{ background: 'white', color: '#666' }}
            >
              No players drafted yet. Click "Draft Player" to build your team.
            </div>
          ) : (
            <div style={{ background: 'white' }}>
              {/* Header */}
              <div
                className="grid gap-2 px-4 py-3 text-xs uppercase tracking-wider"
                style={{
                  gridTemplateColumns: '1fr repeat(4, 4rem) 5rem' + (isOwner ? ' 4rem' : ''),
                  background: '#006747',
                  color: 'white',
                  borderBottom: '2px solid #c9a227',
                }}
              >
                <span>Player</span>
                <span className="text-center">R1</span>
                <span className="text-center">R2</span>
                <span className="text-center">R3</span>
                <span className="text-center">R4</span>
                <span className="text-center">Total</span>
                {isOwner && <span></span>}
              </div>

              {/* Rows */}
              {team.players?.map((teamPlayer, idx) => (
                <div
                  key={teamPlayer.id}
                  className="grid gap-2 px-4 py-4 items-center"
                  style={{
                    gridTemplateColumns: '1fr repeat(4, 4rem) 5rem' + (isOwner ? ' 4rem' : ''),
                    borderBottom: '1px solid #f0f0f0',
                    background: idx % 2 === 0 ? 'white' : '#fafafa',
                  }}
                >
                  <span className="font-medium" style={{ color: '#1a1a1a' }}>
                    {teamPlayer.player.full_name}
                  </span>
                  <span className="text-center" style={getScoreStyle(teamPlayer.scores?.round_1)}>
                    {formatScore(teamPlayer.scores?.round_1)}
                  </span>
                  <span className="text-center" style={getScoreStyle(teamPlayer.scores?.round_2)}>
                    {formatScore(teamPlayer.scores?.round_2)}
                  </span>
                  <span className="text-center" style={getScoreStyle(teamPlayer.scores?.round_3)}>
                    {formatScore(teamPlayer.scores?.round_3)}
                  </span>
                  <span className="text-center" style={getScoreStyle(teamPlayer.scores?.round_4)}>
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
                      className="text-sm text-right"
                      style={{ color: '#c41e3a' }}
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
          <div
            className="fixed inset-0 flex items-center justify-center p-4 z-50"
            style={{ background: 'rgba(0,0,0,0.6)' }}
          >
            <div
              className="w-full max-w-lg max-h-[80vh] overflow-hidden"
              style={{ background: '#fffef7' }}
            >
              <div
                className="px-5 py-4 flex justify-between items-center"
                style={{ background: '#006747', borderBottom: '2px solid #c9a227' }}
              >
                <div>
                  <h2 className="text-lg text-white" style={{ fontFamily: 'Georgia, serif' }}>
                    Draft Player
                  </h2>
                  <p className="text-sm" style={{ color: 'rgba(255,255,255,0.7)' }}>
                    {maxPlayers - draftedCount} slot{maxPlayers - draftedCount !== 1 ? 's' : ''} remaining
                  </p>
                </div>
                <button
                  onClick={() => setShowDraftModal(false)}
                  className="text-white/70 hover:text-white text-2xl leading-none"
                >
                  ×
                </button>
              </div>

              <div className="p-5">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search players..."
                  className="w-full px-4 py-2.5 border text-sm mb-4"
                  style={{ borderColor: '#e5e2d3', outline: 'none' }}
                />

                <div className="overflow-y-auto max-h-[50vh]">
                  {filteredPlayers.length === 0 ? (
                    <p className="text-center py-8" style={{ color: '#888' }}>
                      No available players found.
                    </p>
                  ) : (
                    <div>
                      {filteredPlayers.map((player, index) => (
                        <div
                          key={player.player_id}
                          className="flex justify-between items-center py-3 px-2"
                          style={{
                            borderBottom:
                              index < filteredPlayers.length - 1 ? '1px solid #f0f0f0' : 'none',
                          }}
                        >
                          <div>
                            <p className="font-medium" style={{ color: '#1a1a1a' }}>
                              {player.first_name} {player.last_name}
                            </p>
                            {player.is_amateur && (
                              <span className="text-xs" style={{ color: '#888' }}>
                                Amateur
                              </span>
                            )}
                          </div>
                          <button
                            onClick={() => handleDraftPlayer(player.id)}
                            disabled={drafting}
                            className="px-4 py-1.5 text-sm font-medium disabled:opacity-50"
                            style={{ background: '#006747', color: 'white' }}
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
