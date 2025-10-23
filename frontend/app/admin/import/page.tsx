'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import ErrorMessage from '@/components/ErrorMessage';
import ProtectedRoute from '@/components/ProtectedRoute';
import { tournamentAPI, Tournament } from '@/lib/api';
import { getUser } from '@/lib/auth';

export default function ImportTournamentPage() {
  const [tournId, setTournId] = useState('');
  const [year, setYear] = useState(new Date().getFullYear().toString());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [existingTournaments, setExistingTournaments] = useState<Tournament[]>([]);
  const [loadingTournaments, setLoadingTournaments] = useState(false);
  const [schedule, setSchedule] = useState<Tournament[]>([]);
  const [loadingSchedule, setLoadingSchedule] = useState(false);
  const [selectedTournament, setSelectedTournament] = useState('');
  const router = useRouter();
  const user = getUser();

  // Load existing tournaments and schedule on component mount
  useEffect(() => {
    loadExistingTournaments();
    loadSchedule();
  }, []);

  const loadExistingTournaments = async () => {
    setLoadingTournaments(true);
    try {
      const tournaments = await tournamentAPI.getTournaments();
      setExistingTournaments(tournaments);
    } catch (err) {
      console.error('Failed to load existing tournaments:', err);
    } finally {
      setLoadingTournaments(false);
    }
  };

  const loadSchedule = async () => {
    setLoadingSchedule(true);
    try {
      const scheduleData = await tournamentAPI.getSchedule();
      setSchedule(scheduleData);
    } catch (err) {
      console.error('Failed to load tournament schedule:', err);
    } finally {
      setLoadingSchedule(false);
    }
  };

  const handleTournamentSelect = (tournamentId: string) => {
    const tournament = schedule.find(t => t.id === tournamentId);
    if (tournament) {
      setTournId(tournament.tourn_id);
      setYear(tournament.year.toString());
      setSelectedTournament(tournamentId);
    }
  };

  // Check if user is owner (only owners can import tournaments)
  if (!user?.is_owner) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              <p>You do not have permission to access this page.</p>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      await tournamentAPI.importTournament(tournId, parseInt(year));
      setSuccess(true);
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import tournament');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Import Tournament</h1>
          
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg mb-6">
            <p className="font-medium">⚠️ Development/Test Only</p>
            <p className="text-sm mt-1">In production, tournaments will be imported automatically. This tool is for testing purposes only.</p>
          </div>

          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
            <ErrorMessage message={error} />

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
                <p>Tournament imported successfully! Redirecting...</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="tournamentSelect" className="block text-sm font-medium text-gray-700 mb-1">
                  Select Tournament
                </label>
                {loadingSchedule ? (
                  <div className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50">
                    Loading tournaments...
                  </div>
                ) : (
                  <select
                    id="tournamentSelect"
                    value={selectedTournament}
                    onChange={(e) => handleTournamentSelect(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Choose a tournament...</option>
                    {schedule.map((tournament) => (
                      <option key={tournament.id} value={tournament.id}>
                        {tournament.name} ({tournament.year}) - {tournament.status}
                      </option>
                    ))}
                  </select>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  Select from available tournaments or enter manually below
                </p>
              </div>

              <div>
                <label htmlFor="tournId" className="block text-sm font-medium text-gray-700 mb-1">
                  Tournament ID (Manual Entry)
                </label>
                <input
                  type="text"
                  id="tournId"
                  value={tournId}
                  onChange={(e) => setTournId(e.target.value)}
                  required
                  placeholder="e.g., 475"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  The tournament ID from the Live Golf Data API (e.g., "002", "475")
                </p>
              </div>

              <div>
                <label htmlFor="year" className="block text-sm font-medium text-gray-700 mb-1">
                  Year
                </label>
                <input
                  type="number"
                  id="year"
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                  required
                  min="2020"
                  max="2030"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Importing...' : 'Import Tournament'}
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Instructions:</h3>
              <ol className="list-decimal list-inside text-sm text-gray-600 space-y-1">
                <li>Find the tournament ID from the Golf API schedule</li>
                <li>Enter the tournament ID and year</li>
                <li>Click Import to fetch tournament details and players</li>
                <li>The tournament will be available for creating leagues</li>
              </ol>
            </div>
          </div>

          {/* Existing Tournaments */}
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 mt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Existing Tournaments</h2>
            
            {loadingTournaments ? (
              <p className="text-gray-600">Loading tournaments...</p>
            ) : existingTournaments.length === 0 ? (
              <p className="text-gray-600">No tournaments imported yet.</p>
            ) : (
              <div className="space-y-3">
                {existingTournaments.map((tournament) => (
                  <div key={tournament.id} className="flex justify-between items-center p-3 border border-gray-200 rounded-md">
                    <div>
                      <h3 className="font-medium text-gray-900">{tournament.name}</h3>
                      <p className="text-sm text-gray-600">
                        {tournament.year} • {tournament.start_date} to {tournament.end_date}
                      </p>
                      <p className="text-xs text-gray-500">ID: {tournament.tourn_id}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      tournament.status === 'completed' ? 'bg-green-100 text-green-800' :
                      tournament.status === 'active' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {tournament.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
            
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Quick Import (Common Tournaments):</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <button
                  onClick={() => {
                    setTournId('475');
                    setYear('2024');
                  }}
                  className="text-left p-2 border border-gray-300 rounded-md hover:bg-gray-50 text-sm"
                >
                  Valspar Championship 2024 (ID: 475)
                </button>
                <button
                  onClick={() => {
                    setTournId('002');
                    setYear('2024');
                  }}
                  className="text-left p-2 border border-gray-300 rounded-md hover:bg-gray-50 text-sm"
                >
                  Masters 2024 (ID: 002)
                </button>
                <button
                  onClick={() => {
                    setTournId('016');
                    setYear('2024');
                  }}
                  className="text-left p-2 border border-gray-300 rounded-md hover:bg-gray-50 text-sm"
                >
                  PGA Championship 2024 (ID: 016)
                </button>
                <button
                  onClick={() => {
                    setTournId('026');
                    setYear('2024');
                  }}
                  className="text-left p-2 border border-gray-300 rounded-md hover:bg-gray-50 text-sm"
                >
                  US Open 2024 (ID: 026)
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}

