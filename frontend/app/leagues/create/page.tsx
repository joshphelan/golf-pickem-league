'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
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
  const searchParams = useSearchParams();

  useEffect(() => {
    loadTournaments();
  }, []);

  useEffect(() => {
    // Pre-select tournament from URL parameter
    const preselectedTournament = searchParams.get('tournament');
    if (preselectedTournament && tournaments.length > 0) {
      const tournament = tournaments.find((t) => t.id === preselectedTournament);
      if (tournament) {
        setTournamentId(tournament.id);
        // Auto-set draft deadline to day before tournament starts
        if (tournament.start_date) {
          const startDate = new Date(tournament.start_date);
          startDate.setDate(startDate.getDate() - 1);
          startDate.setHours(23, 59, 0, 0);
          setDraftDeadline(startDate.toISOString().slice(0, 16));
        }
      }
    }
  }, [searchParams, tournaments]);

  const loadTournaments = async () => {
    try {
      const data = await tournamentAPI.getTournaments();
      // Filter to only show upcoming/active tournaments
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
    // Auto-set draft deadline when tournament is selected
    const tournament = tournaments.find((t) => t.id === id);
    if (tournament?.start_date && !draftDeadline) {
      const startDate = new Date(tournament.start_date);
      startDate.setDate(startDate.getDate() - 1);
      startDate.setHours(23, 59, 0, 0);
      setDraftDeadline(startDate.toISOString().slice(0, 16));
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

  const selectedTournament = tournaments.find((t) => t.id === tournamentId);

  return (
    <ProtectedRoute>
      <div className="min-h-screen" style={{ background: '#fffef7' }}>
        <Navbar />
        <div className="max-w-xl mx-auto px-6 py-10">
          <h1
            className="text-2xl mb-8"
            style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}
          >
            Create League
          </h1>

          <div style={{ background: 'white', padding: '2rem' }}>
            <ErrorMessage message={error} />

            {loading ? (
              <LoadingSpinner />
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label
                    htmlFor="name"
                    className="block text-xs uppercase tracking-wider mb-2"
                    style={{ color: '#888' }}
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
                    className="w-full px-3 py-2 border text-sm"
                    style={{ borderColor: '#e5e2d3', outline: 'none' }}
                  />
                </div>

                <div>
                  <label
                    htmlFor="tournament"
                    className="block text-xs uppercase tracking-wider mb-2"
                    style={{ color: '#888' }}
                  >
                    Tournament
                  </label>
                  <select
                    id="tournament"
                    value={tournamentId}
                    onChange={(e) => handleTournamentChange(e.target.value)}
                    required
                    className="w-full px-3 py-2 border text-sm"
                    style={{ borderColor: '#e5e2d3', outline: 'none' }}
                  >
                    <option value="">Select a tournament</option>
                    {tournaments.map((tournament) => (
                      <option key={tournament.id} value={tournament.id}>
                        {tournament.name} -{' '}
                        {tournament.start_date
                          ? format(new Date(tournament.start_date), 'MMM d, yyyy')
                          : tournament.year}
                      </option>
                    ))}
                  </select>
                  {selectedTournament && (
                    <p className="mt-2 text-sm" style={{ color: '#666' }}>
                      {selectedTournament.venue && `${selectedTournament.venue} - `}
                      {selectedTournament.start_date &&
                        format(new Date(selectedTournament.start_date), 'MMM d')}{' '}
                      to{' '}
                      {selectedTournament.end_date &&
                        format(new Date(selectedTournament.end_date), 'MMM d, yyyy')}
                    </p>
                  )}
                </div>

                <div>
                  <label
                    htmlFor="draftDeadline"
                    className="block text-xs uppercase tracking-wider mb-2"
                    style={{ color: '#888' }}
                  >
                    Draft Deadline
                  </label>
                  <div className="grid grid-cols-2 gap-3">
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
                        className="w-full px-3 py-2 border text-sm"
                        style={{ borderColor: '#e5e2d3', outline: 'none' }}
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
                        className="w-full px-3 py-2 border text-sm"
                        style={{ borderColor: '#e5e2d3', outline: 'none' }}
                      />
                    </div>
                  </div>
                  <p className="mt-1 text-xs" style={{ color: '#888' }}>
                    Players must complete their draft before this time
                  </p>
                </div>

                <div>
                  <label
                    htmlFor="teamSize"
                    className="block text-xs uppercase tracking-wider mb-2"
                    style={{ color: '#888' }}
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
                    className="w-24 px-3 py-2 border text-sm"
                    style={{ borderColor: '#e5e2d3', outline: 'none' }}
                  />
                  <span className="ml-2 text-sm" style={{ color: '#666' }}>
                    golfers per team
                  </span>
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-3 text-sm font-medium disabled:opacity-50 transition-opacity"
                  style={{ background: '#006747', color: 'white' }}
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
