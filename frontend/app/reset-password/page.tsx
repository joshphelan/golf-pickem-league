'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { authAPI } from '@/lib/api';
import ErrorMessage from '@/components/ErrorMessage';

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const token = searchParams.get('token') ?? '';

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!token) {
      setError('Invalid reset link. Please request a new one.');
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    setLoading(true);
    try {
      await authAPI.confirmPasswordReset(token, newPassword);
      setSuccess(true);
      setTimeout(() => router.push('/login'), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid or expired reset link. Please request a new one.');
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
        <h2 className="text-lg font-semibold text-center mb-8 text-[var(--charcoal)]">Set New Password</h2>

        {success ? (
          <div className="text-center space-y-4">
            <div className="px-4 py-3 bg-green-50 text-green-700 rounded-xl text-sm">
              Password reset successfully! Redirecting to login...
            </div>
            <Link href="/login" className="block text-sm text-[var(--masters-green)] font-medium hover:underline">
              Go to login
            </Link>
          </div>
        ) : (
          <>
            <ErrorMessage message={error} />
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="newPassword" className="block text-sm font-medium mb-1.5 text-gray-700">
                  New Password
                </label>
                <input
                  type="password"
                  id="newPassword"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                  disabled={!token}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-base sm:text-sm transition-all disabled:opacity-50"
                />
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1.5 text-gray-700">
                  Confirm Password
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={8}
                  disabled={!token}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-base sm:text-sm transition-all disabled:opacity-50"
                />
              </div>

              <button
                type="submit"
                disabled={loading || !token}
                className="w-full font-medium py-2.5 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed text-white bg-[var(--masters-green)] transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-md"
              >
                {loading ? 'Saving...' : 'Set New Password'}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-gray-500">
              <Link href="/forgot-password" className="text-[var(--masters-green)] font-medium hover:underline">
                Request a new reset link
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense>
      <ResetPasswordForm />
    </Suspense>
  );
}
