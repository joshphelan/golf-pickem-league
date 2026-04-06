'use client';

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import ProtectedRoute from '@/components/ProtectedRoute';
import ErrorMessage from '@/components/ErrorMessage';
import { authAPI, User } from '@/lib/api';
import { getUser, setUser } from '@/lib/auth';

export default function ProfilePage() {
  const [user, setUserState] = useState<User | null>(null);
  const [username, setUsername] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const u = getUser();
    if (u) {
      setUserState(u);
      setUsername(u.username);
    }
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (username.trim() === user?.username) return;
    setSaving(true);
    try {
      const updated = await authAPI.updateProfile({ username: username.trim() });
      setUserState(updated);
      setUser(updated);
      setSuccess('Username updated successfully');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update username');
    } finally {
      setSaving(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[var(--cream)]">
        <Navbar />
        <div className="max-w-lg mx-auto px-6 py-10">
          <h1 className="text-2xl mb-8 font-display text-[var(--charcoal)]">Profile</h1>

          <div className="bg-white rounded-xl shadow-sm p-6 sm:p-8">
            <ErrorMessage message={error} />
            {success && (
              <div className="mb-4 px-4 py-2.5 text-sm bg-green-50 text-green-700 rounded-xl">
                {success}
              </div>
            )}

            <form onSubmit={handleSave} className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-xs uppercase tracking-wider mb-2 text-gray-400">
                  Email
                </label>
                <p className="text-sm text-[var(--charcoal)] px-4 py-2.5 bg-[var(--cream)] rounded-lg">
                  {user?.email}
                </p>
              </div>

              <div>
                <label htmlFor="username" className="block text-xs uppercase tracking-wider mb-2 text-gray-400">
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  minLength={3}
                  maxLength={50}
                  className="w-full px-4 py-2.5 border border-[#e5e2d3] rounded-lg text-base sm:text-sm transition-all"
                />
              </div>

              <button
                type="submit"
                disabled={saving || username.trim() === user?.username}
                className="w-full py-3 text-sm font-medium disabled:opacity-50 rounded-lg bg-[var(--masters-green)] text-white transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-md"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
