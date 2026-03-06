'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import ProtectedRoute from '@/components/ProtectedRoute';
import { tournamentAPI, leagueAPI, configAPI, Tournament, League, LiveTournament, PublicConfig } from '@/lib/api';
import { getUser } from '@/lib/auth';
import { format } from 'date-fns';
import { formatScore, getScoreStyle } from '@/lib/formatScore';

export default function DashboardPage() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [myLeagues, setMyLeagues] = useState<League[]>([]);
  const [liveTournament, setLiveTournament] = useState<LiveTournament | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [showPastLeagues, setShowPastLeagues] = useState(false);
  const [config, setConfig] = useState<PublicConfig | null>(null);
  const router = useRouter();
  const user = getUser();

  useEffect(() => {
    loadData();
    configAPI.getPublicConfig().then(setConfig).catch(() => {});
  }, []);

  const loadData = async () => {
    try {
      const [tournamentsData, leaguesData, liveData] = await Promise.all([
        tournamentAPI.getTournaments(),
        leagueAPI.getUserLeagues(),
        tournamentAPI.getLiveTournament().catch(() => null),
      ]);
      setTournaments(tournamentsData);
      setMyLeagues(leaguesData);
      setLiveTournament(liveData);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load data';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinLeague = () => {
    if (joinCode.trim()) {
      router.push(`/leagues/join/${joinCode.trim()}`);
    }
  };

  const activeLeagues = myLeagues.filter(
    (l) => l.tournament?.status === 'active' || l.tournament?.status === 'upcoming'
  );
  const pastLeagues = myLeagues.filter((l) => l.tournament?.status === 'completed');

  const upcomingTournaments = tournaments
    .filter((t) => t.status === 'upcoming' || t.status === 'active')
    .slice(0, 6);

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[var(--cream)]">
        <Navbar />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
          <ErrorMessage message={error} />

          {loading ? (
            <LoadingSpinner />
          ) : (
            <div className="flex flex-col lg:flex-row gap-8">
              {/* Main Content */}
              <div className="flex-1 min-w-0">
                {/* Join League */}
                <div className="mb-8 sm:mb-10 p-5 sm:p-6 flex items-center gap-4 bg-gradient-to-br from-[var(--masters-green)] to-[var(--masters-green-dark)] rounded-xl shadow-md">
                  <div className="flex-1">
                    <p className="text-white text-sm font-medium mb-2">Have an invite code?</p>
                    <div className="flex flex-col sm:flex-row gap-2">
                      <input
                        type="text"
                        value={joinCode}
                        onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                        placeholder="XXXXXXXX"
                        maxLength={8}
                        className="w-full sm:w-36 px-3 py-2 text-sm font-mono tracking-widest border-0 rounded-lg bg-white/95"
                      />
                      <button
                        onClick={handleJoinLeague}
                        disabled={joinCode.length !== 8}
                        className="px-4 py-2 text-sm font-medium disabled:opacity-40 transition-all rounded-lg bg-[var(--masters-gold)] text-[var(--charcoal)] hover:brightness-110"
                      >
                        Join League
                      </button>
                    </div>
                  </div>
                </div>

                {/* My Leagues */}
                <section className="mb-8 sm:mb-10">
                  <div className="flex justify-between items-center mb-5">
                    <h2 className="text-lg font-display text-[var(--charcoal)]">
                      My Leagues
                    </h2>
                    {user?.is_league_admin && (
                      <Link
                        href="/leagues/create"
                        className="text-sm font-medium px-4 py-2 rounded-lg bg-[var(--masters-green)] text-white transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-md"
                      >
                        Create League
                      </Link>
                    )}
                  </div>

                  {activeLeagues.length === 0 && pastLeagues.length === 0 ? (
                    <p className="text-gray-500">You haven&apos;t joined any leagues yet.</p>
                  ) : (
                    <>
                      {/* Active/Upcoming Leagues */}
                      {activeLeagues.length > 0 && (
                        <div className="space-y-3 mb-4">
                          {activeLeagues.map((league) => (
                            <Link
                              key={league.id}
                              href={`/leagues/${league.id}`}
                              className="flex items-center justify-between p-4 bg-white rounded-xl shadow-sm card-hover border-l-[3px]"
                              style={{
                                borderLeftColor:
                                  league.tournament?.status === 'active'
                                    ? 'var(--masters-gold)'
                                    : 'var(--masters-green)',
                              }}
                            >
                              <div>
                                <p className="font-medium text-[var(--charcoal)]">
                                  {league.name}
                                </p>
                                <p className="text-sm text-gray-500">
                                  {league.tournament?.name}
                                  {league.tournament?.start_date && (
                                    <span className="ml-2 text-gray-400">
                                      {format(new Date(league.tournament.start_date), 'MMM d')}
                                    </span>
                                  )}
                                </p>
                              </div>
                              <div className="text-right">
                                {league.tournament?.status === 'active' ? (
                                  <span className="text-xs uppercase tracking-wide font-medium px-3 py-1 rounded-full bg-[var(--masters-gold)] text-[var(--charcoal)]">
                                    LIVE
                                  </span>
                                ) : (
                                  <span className="text-xs uppercase tracking-wide font-medium px-3 py-1 rounded-full bg-green-50 text-green-700">
                                    UPCOMING
                                  </span>
                                )}
                              </div>
                            </Link>
                          ))}
                        </div>
                      )}

                      {/* Past Leagues (Collapsible) */}
                      {pastLeagues.length > 0 && (
                        <div>
                          <button
                            onClick={() => setShowPastLeagues(!showPastLeagues)}
                            className="text-sm flex items-center gap-2 py-2 text-gray-500 hover:text-gray-700 transition-colors"
                          >
                            <span
                              className="inline-block transition-transform duration-200"
                              style={{
                                transform: showPastLeagues ? 'rotate(90deg)' : 'rotate(0)',
                              }}
                            >
                              &#9654;
                            </span>
                            Past Leagues ({pastLeagues.length})
                          </button>
                          {showPastLeagues && (
                            <div className="space-y-2 mt-2">
                              {pastLeagues.map((league) => (
                                <Link
                                  key={league.id}
                                  href={`/leagues/${league.id}`}
                                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border-l-[3px] border-gray-300 transition-all hover:bg-gray-100"
                                >
                                  <div>
                                    <p className="text-gray-600">{league.name}</p>
                                    <p className="text-sm text-gray-400">
                                      {league.tournament?.name}
                                    </p>
                                  </div>
                                  <span className="text-xs uppercase text-gray-400 font-medium px-3 py-1 rounded-full bg-gray-100">
                                    Completed
                                  </span>
                                </Link>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </section>

                {/* Tournaments - For League Admins */}
                {user?.is_league_admin && (
                  <section>
                    <h2 className="text-lg mb-5 font-display text-[var(--charcoal)]">
                      Upcoming Tournaments
                    </h2>

                    {upcomingTournaments.length === 0 ? (
                      <p className="text-gray-500">No upcoming tournaments.</p>
                    ) : (
                      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                        {upcomingTournaments.map((tournament, idx) => (
                          <div
                            key={tournament.id}
                            className="flex items-center gap-4 p-4 transition-colors hover:bg-[var(--cream-dark)]"
                            style={{
                              borderBottom: idx < upcomingTournaments.length - 1 ? '1px solid #f0ede3' : 'none',
                            }}
                          >
                            <div className="text-center w-10 flex-shrink-0 text-[var(--masters-green)]">
                              <p className="text-xs uppercase">
                                {tournament.start_date
                                  ? format(new Date(tournament.start_date), 'MMM')
                                  : ''}
                              </p>
                              <p className="text-lg font-semibold">
                                {tournament.start_date
                                  ? format(new Date(tournament.start_date), 'd')
                                  : '-'}
                              </p>
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-sm sm:text-base text-[var(--charcoal)]">
                                {tournament.name}
                              </p>
                              {tournament.venue && (
                                <p className="text-sm truncate text-gray-400">
                                  {tournament.venue}
                                </p>
                              )}
                            </div>
                            <Link
                              href={`/leagues/create?tournament=${tournament.id}`}
                              className="text-xs sm:text-sm px-3 sm:px-4 py-1.5 rounded-lg bg-[var(--masters-green)] text-white transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-sm flex-shrink-0"
                            >
                              Create League
                            </Link>
                          </div>
                        ))}
                      </div>
                    )}
                  </section>
                )}
              </div>

              {/* Live Tournament Panel */}
              <aside className="w-full lg:w-72 lg:flex-shrink-0">
                <div className="bg-white rounded-xl shadow-sm border border-[#e5e2d3] overflow-hidden sticky top-4">
                  {liveTournament?.tournament ? (
                    <>
                      <div className="px-4 py-3 bg-[var(--masters-green)] border-b-2 border-[var(--masters-gold)]">
                        <div className="flex items-center justify-between">
                          <span className="text-xs uppercase tracking-wider font-medium text-[var(--masters-gold)]">
                            Live
                          </span>
                          <span className="text-xs text-white/70">
                            Round {liveTournament.current_round}
                          </span>
                        </div>
                        <p className="text-white font-medium mt-1 font-display">
                          {liveTournament.tournament.name}
                        </p>
                      </div>
                      <div className="px-4 py-4">
                        <p className="text-xs uppercase tracking-wider mb-3 text-gray-400">
                          Leaderboard
                        </p>
                        {liveTournament.leaderboard.length > 0 ? (
                          <div className="space-y-2.5">
                            {liveTournament.leaderboard.slice(0, 8).map((entry, idx) => (
                              <div
                                key={idx}
                                className="flex items-center justify-between text-sm"
                              >
                                <div className="flex items-center gap-2">
                                  <span className="w-5 text-center text-gray-400 text-xs">
                                    {entry.position || idx + 1}
                                  </span>
                                  <span className="text-[var(--charcoal)]">
                                    {entry.player_name}
                                  </span>
                                </div>
                                <span style={getScoreStyle(entry.total_score)}>
                                  {formatScore(entry.total_score)}
                                </span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-gray-400">
                            No scores yet
                          </p>
                        )}
                      </div>
                      <div className="px-4 py-2.5 text-xs bg-[var(--cream-dark)] text-gray-400 rounded-b-xl">
                        Updates every {config?.sync_interval_minutes ?? 15} min during play
                      </div>
                    </>
                  ) : (
                    <div className="p-6 text-center">
                      <p className="text-sm text-gray-400">
                        No tournament in progress
                      </p>
                      <p className="text-xs mt-1 text-gray-300">
                        Check back during tournament days
                      </p>
                    </div>
                  )}
                </div>
              </aside>
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
