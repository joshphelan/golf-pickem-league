'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import ProtectedRoute from '@/components/ProtectedRoute';
import { tournamentAPI, leagueAPI, Tournament, League } from '@/lib/api';
import { getUser } from '@/lib/auth';
import { format } from 'date-fns';

export default function DashboardPage() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [myLeagues, setMyLeagues] = useState<League[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [showJoinInput, setShowJoinInput] = useState(false);
  const router = useRouter();
  const user = getUser();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [tournamentsData, leaguesData] = await Promise.all([
        tournamentAPI.getTournaments(),
        leagueAPI.getUserLeagues(),
      ]);
      setTournaments(tournamentsData);
      setMyLeagues(leaguesData);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load data';
      setError(errorMsg);
      console.error('Dashboard load error:', err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinLeague = () => {
    if (joinCode.trim()) {
      router.push(`/leagues/join/${joinCode.trim()}`);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

          <ErrorMessage message={error} />

          {loading ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Join League Section - Always Visible */}
              <div className="mb-8">
                <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Want to join a league?
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Enter the invite code you received from the league creator
                  </p>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={joinCode}
                      onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                      placeholder="Enter 8-character invite code"
                      maxLength={8}
                      className="flex-1 px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 font-mono text-lg"
                    />
                    <button
                      onClick={handleJoinLeague}
                      disabled={joinCode.length !== 8}
                      className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-md font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Join League
                    </button>
                  </div>
                </div>
              </div>

              {/* My Leagues Section */}
              <div className="mb-12">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-semibold text-gray-900">My Leagues</h2>
                  {user?.is_league_admin && (
                    <Link
                      href="/leagues/create"
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium"
                    >
                      Create League
                    </Link>
                  )}
                </div>
                
                {!user?.is_league_admin && (
                  <div className="mb-4 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg">
                    <p className="text-sm">
                      💡 To create your own leagues, request League Admin access from an owner.
                    </p>
                  </div>
                )}

                {myLeagues.length === 0 ? (
                  <p className="text-gray-600">You haven't joined any leagues yet.</p>
                ) : (
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {myLeagues.map((league) => (
                      <Link
                        key={league.id}
                        href={`/leagues/${league.id}`}
                        className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
                      >
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {league.name}
                        </h3>
                        <p className="text-sm text-gray-600 mb-1">
                          {league.tournament?.name || 'Tournament'}
                        </p>
                        <p className="text-xs text-gray-500">
                          Draft Deadline:{' '}
                          {format(new Date(league.draft_deadline), 'MMM d, yyyy h:mm a')}
                        </p>
                      </Link>
                    ))}
                  </div>
                )}
              </div>

              {/* Tournaments Section - Owner Only */}
              {user?.is_owner && (
                <div>
                  <div className="mb-4">
                    <h2 className="text-2xl font-semibold text-gray-900">Tournaments</h2>
                  </div>

                  {tournaments.length === 0 ? (
                    <p className="text-gray-600">No tournaments imported yet.</p>
                  ) : (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {tournaments.map((tournament) => (
                        <div
                          key={tournament.id}
                          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
                        >
                          <div className="flex justify-between items-start mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {tournament.name}
                            </h3>
                            <span
                              className={`text-xs font-medium px-2 py-1 rounded ${
                                tournament.status === 'active'
                                  ? 'bg-green-100 text-green-800'
                                  : tournament.status === 'completed'
                                  ? 'bg-gray-100 text-gray-800'
                                  : 'bg-blue-100 text-blue-800'
                              }`}
                            >
                              {tournament.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-1">{tournament.year}</p>
                          {tournament.venue && (
                            <p className="text-xs text-gray-500 mb-1">{tournament.venue}</p>
                          )}
                          {tournament.start_date && tournament.end_date && (
                            <p className="text-xs text-gray-500">
                              {format(new Date(tournament.start_date), 'MMM d')} -{' '}
                              {format(new Date(tournament.end_date), 'MMM d, yyyy')}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}

