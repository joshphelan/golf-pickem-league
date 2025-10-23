'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import ProtectedRoute from '@/components/ProtectedRoute';
import { tournamentAPI, leagueAPI, Tournament } from '@/lib/api';
import { format } from 'date-fns';

export default function CreateLeaguePage() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [name, setName] = useState('');
  const [tournamentId, setTournamentId] = useState('');
  const [draftDeadline, setDraftDeadline] = useState('');
  const [teamSize, setTeamSize] = useState(4);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    loadTournaments();
  }, []);

  const loadTournaments = async () => {
    try {
      const data = await tournamentAPI.getTournaments();
      setTournaments(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load tournaments');
    } finally {
      setLoading(false);
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
      });
      router.push(`/leagues/${league.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create league');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Create League</h1>

          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
            <ErrorMessage message={error} />

            {loading ? (
              <LoadingSpinner />
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                    League Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    placeholder="e.g., Friends & Family Golf League"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label
                    htmlFor="tournament"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Tournament
                  </label>
                  <select
                    id="tournament"
                    value={tournamentId}
                    onChange={(e) => setTournamentId(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select a tournament</option>
                    {tournaments.map((tournament) => (
                      <option key={tournament.id} value={tournament.id}>
                        {tournament.name} ({tournament.year}) - {tournament.status}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="draftDeadline"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Draft Deadline
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="draftDate" className="block text-xs text-gray-600 mb-1">
                        Date
                      </label>
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
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label htmlFor="draftTime" className="block text-xs text-gray-600 mb-1">
                        Time
                      </label>
                      <input
                        type="time"
                        id="draftTime"
                        value={draftDeadline.split('T')[1] || '23:59'}
                        onChange={(e) => {
                          const date = draftDeadline.split('T')[0];
                          setDraftDeadline(`${date}T${e.target.value}`);
                        }}
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    Players can only draft before this deadline (must be in the future)
                  </p>
                </div>

                <div>
                  <label
                    htmlFor="teamSize"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Team Size
                  </label>
                  <input
                    type="number"
                    id="teamSize"
                    value={teamSize}
                    onChange={(e) => setTeamSize(parseInt(e.target.value))}
                    required
                    min="1"
                    max="10"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Number of golfers each team must draft (default: 4)
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
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

