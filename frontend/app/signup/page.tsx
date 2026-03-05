'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authAPI } from '@/lib/api';
import ErrorMessage from '@/components/ErrorMessage';

export default function SignupPage() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    // Validation
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      const response = await authAPI.signup(email, username, password);
      setSuccess(true);
      // Store the success message if available
      if (response.message) {
        localStorage.setItem('signup_message', response.message);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    const message = localStorage.getItem('signup_message') ||
      'Your account has been created successfully. You can now log in!';

    return (
      <div className="min-h-screen flex items-center justify-center px-4" style={{ background: '#fffef7' }}>
        <div className="max-w-md w-full p-8" style={{ background: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <div className="text-center">
            <div
              className="mx-auto flex items-center justify-center h-12 w-12 rounded-full mb-4"
              style={{ background: '#e8f5e9' }}
            >
              <svg
                className="h-6 w-6"
                fill="none"
                stroke="#2e7d32"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-bold mb-2" style={{ color: '#1a1a1a' }}>Account Created!</h2>
            <p className="mb-6" style={{ color: '#666' }}>{message}</p>
            <Link
              href="/login"
              className="inline-block font-medium py-2 px-6 rounded-md text-white transition-opacity hover:opacity-90"
              style={{ background: '#006747' }}
              onClick={() => localStorage.removeItem('signup_message')}
            >
              Go to Login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: '#fffef7' }}>
      <div className="max-w-md w-full p-8" style={{ background: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h1
          className="text-3xl text-center mb-6"
          style={{ fontFamily: 'Georgia, serif', color: '#006747' }}
        >
          Golf Pick&apos;em League
        </h1>
        <h2 className="text-xl font-semibold text-center mb-6" style={{ color: '#1a1a1a' }}>Sign Up</h2>

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
              style={{ borderColor: '#d1d5db' }}
            />
          </div>

          <div>
            <label htmlFor="username" className="block text-sm font-medium mb-1" style={{ color: '#333' }}>
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2"
              style={{ borderColor: '#d1d5db' }}
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
              minLength={8}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2"
              style={{ borderColor: '#d1d5db' }}
            />
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium mb-1"
              style={{ color: '#333' }}
            >
              Confirm Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={8}
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
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm" style={{ color: '#666' }}>
          Already have an account?{' '}
          <Link href="/login" className="hover:underline" style={{ color: '#006747' }}>
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
