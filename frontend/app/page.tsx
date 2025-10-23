'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { isAuthenticated } from '@/lib/auth';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated()) {
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Golf Pickem League
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Join fantasy golf leagues, draft PGA Tour players, and compete with friends
          </p>

          <div className="flex justify-center space-x-4">
            <Link
              href="/login"
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-8 rounded-lg text-lg"
            >
              Login
            </Link>
            <Link
              href="/signup"
              className="bg-white hover:bg-gray-50 text-blue-600 border-2 border-blue-600 font-medium py-3 px-8 rounded-lg text-lg"
            >
              Sign Up
            </Link>
          </div>

          <div className="mt-16 grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-3xl mb-2">🏌️</div>
              <h3 className="text-lg font-semibold mb-2">Draft Players</h3>
              <p className="text-gray-600">
                Build your team by drafting PGA Tour players before tournament deadlines
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-3xl mb-2">📊</div>
              <h3 className="text-lg font-semibold mb-2">Track Scores</h3>
              <p className="text-gray-600">
                Follow real-time tournament scores and watch your team compete
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-3xl mb-2">🏆</div>
              <h3 className="text-lg font-semibold mb-2">Win Leagues</h3>
              <p className="text-gray-600">
                Compete in private leagues with friends for bragging rights
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
