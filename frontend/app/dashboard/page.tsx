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

  // Separate active/upcoming from completed leagues
  const activeLeagues = myLeagues.filter(
    (l) => l.tournament?.status === 'active' || l.tournament?.status === 'upcoming'
  );
  const pastLeagues = myLeagues.filter((l) => l.tournament?.status === 'completed');

  // Filter tournaments for display
  const upcomingTournaments = tournaments
    .filter((t) => t.status === 'upcoming' || t.status === 'active')
    .slice(0, 6);

  return (
    <ProtectedRoute>
      <div className="min-h-screen" style={{ background: '#fffef7' }}>
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
                <div
                  className="mb-6 sm:mb-10 p-4 sm:p-5 flex items-center gap-4"
                  style={{
                    background: 'linear-gradient(135deg, #006747 0%, #004d35 100%)',
                    borderRadius: '2px',
                  }}
                >
                  <div className="flex-1">
                    <p className="text-white text-sm font-medium mb-1">Have an invite code?</p>
                    <div className="flex flex-col sm:flex-row gap-2">
                      <input
                        type="text"
                        value={joinCode}
                        onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                        placeholder="XXXXXXXX"
                        maxLength={8}
                        className="w-full sm:w-36 px-3 py-2 text-sm font-mono tracking-widest border-0"
                        style={{ background: 'rgba(255,255,255,0.95)' }}
                      />
                      <button
                        onClick={handleJoinLeague}
                        disabled={joinCode.length !== 8}
                        className="px-4 py-2 text-sm font-medium disabled:opacity-40 transition-opacity"
                        style={{ background: '#c9a227', color: '#1a1a1a' }}
                      >
                        Join League
                      </button>
                    </div>
                  </div>
                </div>

                {/* My Leagues */}
                <section className="mb-6 sm:mb-10">
                  <div className="flex justify-between items-center mb-4">
                    <h2
                      className="text-lg"
                      style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}
                    >
                      My Leagues
                    </h2>
                    {user?.is_league_admin && (
                      <Link
                        href="/leagues/create"
                        className="text-sm font-medium px-4 py-2"
                        style={{ background: '#006747', color: 'white' }}
                      >
                        Create League
                      </Link>
                    )}
                  </div>

                  {activeLeagues.length === 0 && pastLeagues.length === 0 ? (
                    <p style={{ color: '#666' }}>You haven't joined any leagues yet.</p>
                  ) : (
                    <>
                      {/* Active/Upcoming Leagues */}
                      {activeLeagues.length > 0 && (
                        <div className="space-y-2 mb-4">
                          {activeLeagues.map((league) => (
                            <Link
                              key={league.id}
                              href={`/leagues/${league.id}`}
                              className="flex items-center justify-between p-4 transition-all hover:translate-x-1"
                              style={{
                                background: 'white',
                                borderLeft:
                                  league.tournament?.status === 'active'
                                    ? '3px solid #c9a227'
                                    : '3px solid #006747',
                              }}
                            >
                              <div>
                                <p className="font-medium" style={{ color: '#1a1a1a' }}>
                                  {league.name}
                                </p>
                                <p className="text-sm" style={{ color: '#666' }}>
                                  {league.tournament?.name}
                                  {league.tournament?.start_date && (
                                    <span className="ml-2" style={{ color: '#888' }}>
                                      {format(new Date(league.tournament.start_date), 'MMM d')}
                                    </span>
                                  )}
                                </p>
                              </div>
                              <div className="text-right">
                                <span
                                  className="text-xs uppercase tracking-wide px-2 py-1"
                                  style={{
                                    background:
                                      league.tournament?.status === 'active'
                                        ? '#c9a227'
                                        : '#e8f5e9',
                                    color:
                                      league.tournament?.status === 'active' ? '#1a1a1a' : '#2e7d32',
                                  }}
                                >
                                  {league.tournament?.status === 'active' ? 'LIVE' : 'UPCOMING'}
                                </span>
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
                            className="text-sm flex items-center gap-2 py-2"
                            style={{ color: '#666' }}
                          >
                            <span
                              style={{
                                transform: showPastLeagues ? 'rotate(90deg)' : 'rotate(0)',
                                transition: 'transform 0.2s',
                                display: 'inline-block',
                              }}
                            >
                              ▶
                            </span>
                            Past Leagues ({pastLeagues.length})
                          </button>
                          {showPastLeagues && (
                            <div className="space-y-2 mt-2">
                              {pastLeagues.map((league) => (
                                <Link
                                  key={league.id}
                                  href={`/leagues/${league.id}`}
                                  className="flex items-center justify-between p-4 transition-opacity hover:opacity-80"
                                  style={{
                                    background: '#f5f5f5',
                                    borderLeft: '3px solid #ccc',
                                  }}
                                >
                                  <div>
                                    <p style={{ color: '#666' }}>{league.name}</p>
                                    <p className="text-sm" style={{ color: '#888' }}>
                                      {league.tournament?.name}
                                    </p>
                                  </div>
                                  <span
                                    className="text-xs uppercase"
                                    style={{ color: '#888' }}
                                  >
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
                    <h2
                      className="text-lg mb-4"
                      style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}
                    >
                      Upcoming Tournaments
                    </h2>

                    {upcomingTournaments.length === 0 ? (
                      <p style={{ color: '#666' }}>No upcoming tournaments.</p>
                    ) : (
                      <div className="space-y-1">
                        {upcomingTournaments.map((tournament) => (
                          <div
                            key={tournament.id}
                            className="flex items-center gap-3 p-3"
                            style={{
                              background: 'white',
                              borderBottom: '1px solid #f0f0f0',
                            }}
                          >
                            <div
                              className="text-center w-10 flex-shrink-0"
                              style={{ color: '#006747' }}
                            >
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
                              <p className="font-medium text-sm sm:text-base" style={{ color: '#1a1a1a' }}>
                                {tournament.name}
                              </p>
                              {tournament.venue && (
                                <p className="text-sm truncate" style={{ color: '#888' }}>
                                  {tournament.venue}
                                </p>
                              )}
                            </div>
                            <Link
                              href={`/leagues/create?tournament=${tournament.id}`}
                              className="text-xs sm:text-sm px-2 sm:px-3 py-1.5 transition-colors hover:opacity-80 flex-shrink-0"
                              style={{
                                background: '#006747',
                                color: 'white',
                              }}
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
                <div
                  style={{
                    background: 'white',
                    border: '1px solid #e5e2d3',
                    position: 'sticky',
                    top: '1rem',
                  }}
                >
                  {liveTournament?.tournament ? (
                    <>
                      <div
                        className="px-4 py-3"
                        style={{
                          background: '#006747',
                          borderBottom: '2px solid #c9a227',
                        }}
                      >
                        <div className="flex items-center justify-between">
                          <span
                            className="text-xs uppercase tracking-wider"
                            style={{ color: '#c9a227' }}
                          >
                            Live
                          </span>
                          <span className="text-xs text-white/70">
                            Round {liveTournament.current_round}
                          </span>
                        </div>
                        <p
                          className="text-white font-medium mt-1"
                          style={{ fontFamily: 'Georgia, serif' }}
                        >
                          {liveTournament.tournament.name}
                        </p>
                      </div>
                      <div className="px-4 py-3">
                        <p
                          className="text-xs uppercase tracking-wider mb-3"
                          style={{ color: '#888' }}
                        >
                          Leaderboard
                        </p>
                        {liveTournament.leaderboard.length > 0 ? (
                          <div className="space-y-2">
                            {liveTournament.leaderboard.slice(0, 8).map((entry, idx) => (
                              <div
                                key={idx}
                                className="flex items-center justify-between text-sm"
                              >
                                <div className="flex items-center gap-2">
                                  <span
                                    className="w-5 text-center"
                                    style={{ color: '#888' }}
                                  >
                                    {entry.position || idx + 1}
                                  </span>
                                  <span style={{ color: '#1a1a1a' }}>
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
                          <p className="text-sm" style={{ color: '#888' }}>
                            No scores yet
                          </p>
                        )}
                      </div>
                      <div
                        className="px-4 py-2 text-xs"
                        style={{ background: '#fafafa', color: '#888' }}
                      >
                        Updates every {config?.sync_interval_minutes ?? 15} min during play
                      </div>
                    </>
                  ) : (
                    <div className="p-4 text-center">
                      <p className="text-sm" style={{ color: '#888' }}>
                        No tournament in progress
                      </p>
                      <p className="text-xs mt-1" style={{ color: '#aaa' }}>
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
