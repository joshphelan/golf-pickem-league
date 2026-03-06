'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import ProtectedRoute from '@/components/ProtectedRoute';
import { leagueAPI } from '@/lib/api';

export default function JoinLeaguePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();
  const params = useParams();
  const code = params.code as string;

  const handleJoin = async () => {
    setError('');
    setLoading(true);

    try {
      const result = await leagueAPI.joinLeague(code);
      router.push(`/leagues/${result.league.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to join league');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[var(--cream)]">
        <Navbar />
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-2xl font-display text-[var(--charcoal)] mb-8">Join League</h1>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-[#e5e2d3]">
            <ErrorMessage message={error} />

            <div className="text-center">
              <p className="text-gray-500 mb-6">
                You&apos;re about to join a league with invite code:
              </p>
              <p className="text-2xl font-mono font-bold text-[var(--masters-green)] mb-8">{code}</p>

              <button
                onClick={handleJoin}
                disabled={loading}
                className="font-medium py-3 px-8 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed bg-[var(--masters-green)] text-white transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-md"
              >
                {loading ? 'Joining...' : 'Join League'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
