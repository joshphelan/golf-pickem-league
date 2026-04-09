'use client';

import { useState } from 'react';
import Link from 'next/link';
import { authAPI } from '@/lib/api';
import ErrorMessage from '@/components/ErrorMessage';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authAPI.requestPasswordReset(email);
      setSubmitted(true);
    } catch {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-[var(--cream)]">
      <div className="max-w-md w-full p-8 sm:p-10 bg-white rounded-2xl shadow-lg">
        <h1 className="text-2xl sm:text-3xl text-center mb-2 font-display text-[var(--masters-green)]">
          Golf Pick&apos;em League
        </h1>
        <h2 className="text-lg font-semibold text-center mb-8 text-[var(--charcoal)]">Reset Password</h2>

        {submitted ? (
          <div className="text-center space-y-4">
            <div className="px-4 py-3 bg-green-50 text-green-700 rounded-xl text-sm">
              If an account with that email exists, a password reset link has been sent. Check your inbox.
            </div>
            <Link href="/login" className="block text-sm text-[var(--masters-green)] font-medium hover:underline">
              Back to login
            </Link>
          </div>
        ) : (
          <>
            <ErrorMessage message={error} />
            <p className="text-sm text-gray-500 mb-6">
              Enter your email address and we&apos;ll send you a link to reset your password.
            </p>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-1.5 text-gray-700">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-base sm:text-sm transition-all"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full font-medium py-2.5 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed text-white bg-[var(--masters-green)] transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-md"
              >
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-gray-500">
              <Link href="/login" className="text-[var(--masters-green)] font-medium hover:underline">
                Back to login
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
