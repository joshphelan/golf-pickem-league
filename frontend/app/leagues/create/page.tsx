'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import ProtectedRoute from '@/components/ProtectedRoute';
import { tournamentAPI, leagueAPI, Tournament } from '@/lib/api';
import { format } from 'date-fns';
import { parseLocalDate } from '@/lib/parseDate';

function CreateLeagueForm() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [name, setName] = useState('');
  const [tournamentId, setTournamentId] = useState('');
  const [draftDeadline, setDraftDeadline] = useState('');
  const [teamSize, setTeamSize] = useState(4);
  const [scoringCount, setScoringCount] = useState(4);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    loadTournaments();
  }, []);

  useEffect(() => {
    const preselectedTournament = searchParams.get('tournament');
    if (preselectedTournament && tournaments.length > 0) {
      const tournament = tournaments.find((t) => t.id === preselectedTournament);
      if (tournament) {
        setTournamentId(tournament.id);
        if (tournament.start_date) {
          const startDate = parseLocalDate(tournament.start_date);
          startDate.setDate(startDate.getDate() - 1);
          startDate.setHours(23, 59, 0, 0);
          setDraftDeadline(format(startDate, "yyyy-MM-dd'T'HH:mm"));
        }
      }
    }
  }, [searchParams, tournaments]);

  const loadTournaments = async () => {
    try {
      const data = await tournamentAPI.getTournaments();
      const availableTournaments = data.filter(
        (t) => t.status === 'upcoming' || t.status === 'active'
      );
      setTournaments(availableTournaments);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load tournaments');
    } finally {
      setLoading(false);
    }
  };

  const handleTournamentChange = (id: string) => {
    setTournamentId(id);
    const tournament = tournaments.find((t) => t.id === id);
    if (tournament?.start_date && !draftDeadline) {
      const startDate = parseLocalDate(tournament.start_date);
      startDate.setDate(startDate.getDate() - 1);
      startDate.setHours(23, 59, 0, 0);
      setDraftDeadline(format(startDate, "yyyy-MM-dd'T'HH:mm"));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const league = await leagueAPI.createLeague({
        name,
        tournament_id: tournamentId,
        draft_deadline: new Date(draftDeadline).toISOString(),
        team_size: teamSize,
        scoring_count: scoringCount,
      });
      router.push(`/leagues/${league.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create league');
    } finally {
      setSubmitting(false);
    }
  };

  const selectedTournament = tournaments.find((t) => t.id === tournamentId);

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[var(--cream)]">
        <Navbar />
        <div className="max-w-xl mx-auto px-6 py-10">
          <h1 className="text-2xl mb-8 font-display text-[var(--charcoal)]">
            Create League
          </h1>

          <div className="bg-white rounded-xl shadow-sm p-6 sm:p-8">
            <ErrorMessage message={error} />

            {loading ? (
              <LoadingSpinner />
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label
                    htmlFor="name"
                    className="block text-xs uppercase tracking-wider mb-2 text-gray-400"
                  >
                    League Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    placeholder="e.g., Friends & Family Golf League"
                    className="w-full px-4 py-2.5 border border-[#e5e2d3] rounded-lg text-base sm:text-sm transition-all"
                  />
                </div>

                <div>
                  <label
                    htmlFor="tournament"
                    className="block text-xs uppercase tracking-wider mb-2 text-gray-400"
                  >
                    Tournament
                  </label>
                  <select
                    id="tournament"
                    value={tournamentId}
                    onChange={(e) => handleTournamentChange(e.target.value)}
                    required
                    className="w-full px-4 py-2.5 border border-[#e5e2d3] rounded-lg text-base sm:text-sm transition-all"
                  >
                    <option value="">Select a tournament</option>
                    {tournaments.map((tournament) => (
                      <option key={tournament.id} value={tournament.id}>
                        {tournament.name} -{' '}
                        {tournament.start_date
                          ? format(parseLocalDate(tournament.start_date), 'MMM d, yyyy')
                          : tournament.year}
                      </option>
                    ))}
                  </select>
                  {selectedTournament && (
                    <p className="mt-2 text-sm text-gray-500">
                      {selectedTournament.venue && `${selectedTournament.venue} - `}
                      {selectedTournament.start_date &&
                        format(parseLocalDate(selectedTournament.start_date), 'MMM d')}{' '}
                      to{' '}
                      {selectedTournament.end_date &&
                        format(parseLocalDate(selectedTournament.end_date), 'MMM d, yyyy')}
                    </p>
                  )}
                </div>

                <div>
                  <label
                    htmlFor="draftDeadline"
                    className="block text-xs uppercase tracking-wider mb-2 text-gray-400"
                  >
                    Draft Deadline
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <input
                        type="date"
                        id="draftDate"
                        value={draftDeadline.split('T')[0]}
                        onChange={(e) => {
                          const time = draftDeadline.split('T')[1] || '23:59';
                          setDraftDeadline(`${e.target.value}T${time}`);
                        }}
                        required
                        min={new Date().toISOString().split('T')[0]}
                        className="w-full px-4 py-2.5 border border-[#e5e2d3] rounded-lg text-base sm:text-sm transition-all"
                      />
                    </div>
                    <div>
                      <input
                        type="time"
                        id="draftTime"
                        value={draftDeadline.split('T')[1] || '23:59'}
                        onChange={(e) => {
                          const date = draftDeadline.split('T')[0];
                          setDraftDeadline(`${date}T${e.target.value}`);
                        }}
                        required
                        className="w-full px-4 py-2.5 border border-[#e5e2d3] rounded-lg text-base sm:text-sm transition-all"
                      />
                    </div>
                  </div>
                  <p className="mt-1.5 text-xs text-gray-400">
                    Players must complete their draft before this time
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label
                      htmlFor="teamSize"
                      className="block text-xs uppercase tracking-wider mb-2 text-gray-400"
                    >
                      Picks per Team
                    </label>
                    <select
                      id="teamSize"
                      value={teamSize}
                      onChange={(e) => {
                        const val = parseInt(e.target.value);
                        setTeamSize(val);
                        if (scoringCount > val) setScoringCount(val);
                      }}
                      required
                      className="w-full px-4 py-2.5 border border-[#e5e2d3] rounded-lg text-base sm:text-sm transition-all"
                    >
                      {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
                        <option key={n} value={n}>{n} golfers</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label
                      htmlFor="scoringCount"
                      className="block text-xs uppercase tracking-wider mb-2 text-gray-400"
                    >
                      Scores That Count
                    </label>
                    <select
                      id="scoringCount"
                      value={scoringCount}
                      onChange={(e) => setScoringCount(parseInt(e.target.value))}
                      required
                      className="w-full px-4 py-2.5 border border-[#e5e2d3] rounded-lg text-base sm:text-sm transition-all"
                    >
                      {Array.from({ length: teamSize }, (_, i) => i + 1).map((n) => (
                        <option key={n} value={n}>{n} best score{n > 1 ? 's' : ''}</option>
                      ))}
                    </select>
                  </div>
                </div>
                {scoringCount < teamSize && (
                  <p className="text-xs text-gray-400 -mt-2">
                    Pick {teamSize}, count only the best {scoringCount} scores
                  </p>
                )}

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-3 text-sm font-medium disabled:opacity-50 rounded-lg bg-[var(--masters-green)] text-white transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-md"
                >
                  {submitting ? 'Creating League...' : 'Create League'}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}

export default function CreateLeaguePage() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <CreateLeagueForm />
    </Suspense>
  );
}
