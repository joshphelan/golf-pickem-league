'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authAPI } from '@/lib/api';
import { setToken, setUser } from '@/lib/auth';
import ErrorMessage from '@/components/ErrorMessage';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await authAPI.login(email, password);
      setToken(data.access_token);

      // Fetch user data
      const user = await authAPI.getCurrentUser();
      setUser(user);

      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: '#fffef7' }}>
      <div className="max-w-md w-full p-8" style={{ background: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h1
          className="text-3xl text-center mb-6"
          style={{ fontFamily: 'Georgia, serif', color: '#006747' }}
        >
          Golf Pick&apos;em League
        </h1>
        <h2 className="text-xl font-semibold text-center mb-6" style={{ color: '#1a1a1a' }}>Login</h2>

        <ErrorMessage message={error} />

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-1" style={{ color: '#333' }}>
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2"
              style={{ borderColor: '#d1d5db', focusRingColor: '#006747' }}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-1" style={{ color: '#333' }}>
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2"
              style={{ borderColor: '#d1d5db' }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full font-medium py-2 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed text-white transition-opacity hover:opacity-90"
            style={{ background: '#006747' }}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm" style={{ color: '#666' }}>
          Don&apos;t have an account?{' '}
          <Link href="/signup" className="hover:underline" style={{ color: '#006747' }}>
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
