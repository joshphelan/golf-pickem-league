'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import ProtectedRoute from '@/components/ProtectedRoute';
import { leagueAPI, tournamentAPI, League, LeagueStanding } from '@/lib/api';
import { getUser } from '@/lib/auth';
import { format } from 'date-fns';

export default function LeagueDetailsPage() {
  const [league, setLeague] = useState<League | null>(null);
  const [standings, setStandings] = useState<LeagueStanding[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [showInviteCode, setShowInviteCode] = useState(false);
  const params = useParams();
  const leagueId = params.id as string;
  const user = getUser();

  useEffect(() => {
    loadLeagueData();
  }, []);

  const loadLeagueData = async () => {
    try {
      const [leagueData, standingsData] = await Promise.all([
        leagueAPI.getLeague(leagueId),
        leagueAPI.getLeagueStandings(leagueId), // Auto-detects latest round
      ]);
      setLeague(leagueData);
      setStandings(standingsData.standings || []);
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
      setSuccessMessage('Scores synced successfully!');
      // Reload standings
      const standingsData = await leagueAPI.getLeagueStandings(leagueId); // Auto-detects latest round
      setStandings(standingsData.standings || []);
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

  const copyInviteCode = () => {
    if (league) {
      navigator.clipboard.writeText(league.invite_code);
      alert('Invite code copied to clipboard!');
    }
  };

  // Check if user is league admin (creator) OR has owner role
  const isLeagueOwner = user?.id === league?.admin_id || user?.is_owner;

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {loading ? (
            <LoadingSpinner />
          ) : !league ? (
            <ErrorMessage message="League not found" />
          ) : (
            <>
              <div className="mb-8 flex justify-between items-start">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">{league.name}</h1>
                  <p className="text-gray-600">
                    {league.tournament?.name} ({league.tournament?.year})
                  </p>
                </div>
                {/* Find user's team and link to draft page */}
                {(() => {
                  const userTeam = standings.find(s => s.owner_name === user?.username);
                  return userTeam ? (
                    <Link
                      href={`/teams/${userTeam.team_id}`}
                      className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-md font-semibold text-lg shadow-lg"
                    >
                      🏌️ Draft Your Team
                    </Link>
                  ) : null;
                })()}
              </div>

              <ErrorMessage message={error} />
              {successMessage && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
                  <p>{successMessage}</p>
                </div>
              )}

              {/* League Info */}
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">League Information</h2>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Draft Deadline</p>
                    <p className="font-medium">
                      {format(new Date(league.draft_deadline), 'MMM d, yyyy h:mm a')}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Team Size</p>
                    <p className="font-medium">{league.team_size} golfers per team</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Invite Code</p>
                    <div className="flex items-center space-x-2">
                      <p className="font-mono font-bold text-blue-600">{league.invite_code}</p>
                      <button
                        onClick={copyInviteCode}
                        className="text-sm text-blue-600 hover:underline"
                      >
                        Copy
                      </button>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Tournament Status</p>
                    <p className="font-medium capitalize">{league.tournament?.status}</p>
                  </div>
                </div>

                {isLeagueOwner && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex gap-3">
                      <button
                        onClick={handleSyncScores}
                        disabled={syncing}
                        className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-6 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {syncing ? 'Syncing...' : 'Sync Scores'}
                      </button>
                      {league.tournament?.status === 'upcoming' && (
                        <button
                          onClick={handleRefreshPlayers}
                          disabled={refreshing}
                          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {refreshing ? 'Refreshing...' : 'Refresh Players'}
                        </button>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      League admin/owner: Manually sync tournament scores or refresh player field
                    </p>
                  </div>
                )}
              </div>

              {/* Standings */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900">Standings</h2>
                </div>
                {standings.length === 0 ? (
                  <p className="px-6 py-4 text-gray-600">No teams have drafted players yet.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Rank
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Team
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Owner
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Score
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Players
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {standings.map((standing) => (
                          <tr key={standing.team_id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              #{standing.rank}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Link
                                href={`/teams/${standing.team_id}`}
                                className="text-sm text-blue-600 hover:underline font-medium"
                              >
                                {standing.team_name}
                              </Link>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              {standing.owner_name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                              {standing.total_score !== null ? standing.total_score : 'N/A'}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-600">
                              <div className="space-y-1">
                                {standing.players.map((player) => (
                                  <div key={player.player_id} className="flex justify-between">
                                    <span>{player.name}</span>
                                    <span className="font-medium ml-2">
                                      {player.score !== null ? player.score : '-'}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}

