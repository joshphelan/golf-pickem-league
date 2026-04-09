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

  // Change password state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [pwSaving, setPwSaving] = useState(false);
  const [pwError, setPwError] = useState('');
  const [pwSuccess, setPwSuccess] = useState('');

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

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwError('');
    setPwSuccess('');

    if (newPassword !== confirmNewPassword) {
      setPwError('New passwords do not match.');
      return;
    }
    if (newPassword.length < 8) {
      setPwError('New password must be at least 8 characters.');
      return;
    }

    setPwSaving(true);
    try {
      await authAPI.changePassword(currentPassword, newPassword);
      setPwSuccess('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
    } catch (err: any) {
      setPwError(err.response?.data?.detail || 'Failed to change password');
    } finally {
      setPwSaving(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[var(--cream)]">
        <Navbar />
        <div className="max-w-lg mx-auto px-6 py-10">
          <h1 className="text-2xl mb-8 font-display text-[var(--charcoal)]">Profile</h1>

          {/* Username section */}
          <div className="bg-white rounded-xl shadow-sm p-6 sm:p-8 mb-6">
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

          {/* Change password section */}
          <div className="bg-white rounded-xl shadow-sm p-6 sm:p-8">
            <h2 className="text-base font-semibold text-[var(--charcoal)] mb-5">Change Password</h2>

            {pwError && <ErrorMessage message={pwError} />}
            {pwSuccess && (
              <div className="mb-4 px-4 py-2.5 text-sm bg-green-50 text-green-700 rounded-xl">
                {pwSuccess}
              </div>
            )}

            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label htmlFor="currentPassword" className="block text-xs uppercase tracking-wider mb-2 text-gray-400">
                  Current Password
                </label>
                <input
                  type="password"
                  id="currentPassword"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                  className="w-full px-4 py-2.5 border border-[#e5e2d3] rounded-lg text-base sm:text-sm transition-all"
                />
              </div>

              <div>
                <label htmlFor="newPassword" className="block text-xs uppercase tracking-wider mb-2 text-gray-400">
                  New Password
                </label>
                <input
                  type="password"
                  id="newPassword"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full px-4 py-2.5 border border-[#e5e2d3] rounded-lg text-base sm:text-sm transition-all"
                />
              </div>

              <div>
                <label htmlFor="confirmNewPassword" className="block text-xs uppercase tracking-wider mb-2 text-gray-400">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  id="confirmNewPassword"
                  value={confirmNewPassword}
                  onChange={(e) => setConfirmNewPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full px-4 py-2.5 border border-[#e5e2d3] rounded-lg text-base sm:text-sm transition-all"
                />
              </div>

              <button
                type="submit"
                disabled={pwSaving}
                className="w-full py-3 text-sm font-medium disabled:opacity-50 rounded-lg bg-[var(--masters-green)] text-white transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-md"
              >
                {pwSaving ? 'Saving...' : 'Change Password'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
