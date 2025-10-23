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
  const params = useParams();
  const teamId = params.id as string;
  const user = getUser();

  useEffect(() => {
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
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load team data');
    } finally {
      setLoading(false);
    }
  };

  const loadAvailablePlayers = async () => {
    if (!team?.league_id) return;

    try {
      // Fetch league to get tournament_id
      const leagueData = await leagueAPI.getLeague(team.league_id);
      if (!leagueData.tournament_id) {
        setError('League has no associated tournament');
        return;
      }
      
      const players = await tournamentAPI.getAvailablePlayers(
        leagueData.tournament_id, // Correct tournament_id
        team.league_id            // Correct league_id
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
      setSuccessMessage('Player drafted successfully!');
      await loadTeamData();
      await loadAvailablePlayers();
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
      setSuccessMessage('Player removed from team');
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
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <LoadingSpinner />
        </div>
      </ProtectedRoute>
    );
  }

  if (!team) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <ErrorMessage message="Team not found" />
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  const isOwner = user?.id === team.user_id;
  const draftedCount = team.players?.length || 0;
  const maxPlayers = 4; // TODO: Get from league.team_size
  const canDraft = isOwner && draftedCount < maxPlayers;

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{team.name}</h1>
            <p className="text-gray-600">Owner: {team.owner?.username || team.owner?.email}</p>
          </div>

          <ErrorMessage message={error} />
          {successMessage && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
              <p>{successMessage}</p>
            </div>
          )}

          {/* Team Score */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Team Score</h2>
            <div className="text-4xl font-bold text-blue-600">
              {team.total_score !== null && team.total_score !== undefined
                ? team.total_score
                : 'N/A'}
            </div>
            <p className="text-sm text-gray-600 mt-2">
              {draftedCount} / {maxPlayers} players drafted
            </p>
          </div>

          {/* Drafted Players */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Drafted Players</h2>
              {canDraft && (
                <button
                  onClick={openDraftModal}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium"
                >
                  Draft Player
                </button>
              )}
            </div>

            {draftedCount === 0 ? (
              <p className="px-6 py-4 text-gray-600">No players drafted yet.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Player
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Round 1
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Round 2
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Round 3
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Round 4
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total
                      </th>
                      {isOwner && (
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {team.players?.map((player) => (
                      <tr key={player.player_id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {player.first_name} {player.last_name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {player.scores?.round_1 !== null && player.scores?.round_1 !== undefined
                            ? player.scores.round_1
                            : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {player.scores?.round_2 !== null && player.scores?.round_2 !== undefined
                            ? player.scores.round_2
                            : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {player.scores?.round_3 !== null && player.scores?.round_3 !== undefined
                            ? player.scores.round_3
                            : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {player.scores?.round_4 !== null && player.scores?.round_4 !== undefined
                            ? player.scores.round_4
                            : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                          {player.scores?.total_score !== null &&
                          player.scores?.total_score !== undefined
                            ? player.scores.total_score
                            : '-'}
                        </td>
                        {isOwner && (
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <button
                              onClick={() => handleUndraftPlayer(player.player_id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              Remove
                            </button>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Back to League */}
          <Link
            href={`/leagues/${team.league_id}`}
            className="text-blue-600 hover:underline"
          >
            ← Back to League
          </Link>
        </div>

        {/* Draft Modal */}
        {showDraftModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-2xl font-semibold text-gray-900">Draft Player</h2>
                <button
                  onClick={() => setShowDraftModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              <div className="p-6">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search players..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
                />

                <div className="overflow-y-auto max-h-[50vh]">
                  {filteredPlayers.length === 0 ? (
                    <p className="text-gray-600">No available players found.</p>
                  ) : (
                    <div className="space-y-2">
                      {filteredPlayers.map((player) => (
                        <div
                          key={player.player_id}
                          className="flex justify-between items-center p-3 border border-gray-200 rounded-md hover:bg-gray-50"
                        >
                          <div>
                            <p className="font-medium text-gray-900">
                              {player.first_name} {player.last_name}
                            </p>
                            {player.is_amateur && (
                              <span className="text-xs text-gray-500">(Amateur)</span>
                            )}
                          </div>
                          <button
                            onClick={() => handleDraftPlayer(player.player_id)}
                            disabled={drafting}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {drafting ? 'Drafting...' : 'Draft'}
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

