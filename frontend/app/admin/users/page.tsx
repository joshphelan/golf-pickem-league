'use client';

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import ProtectedRoute from '@/components/ProtectedRoute';
import api from '@/lib/api';
import { getUser } from '@/lib/auth';
import { format } from 'date-fns';

interface User {
  id: string;
  email: string;
  username: string;
  is_approved: boolean;
  is_league_admin: boolean;
  is_owner: boolean;
  is_primary_owner: boolean;
  created_at: string;
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [processingUserId, setProcessingUserId] = useState<string | null>(null);
  const currentUser = getUser();

  // Check if user is owner
  if (!currentUser?.is_owner) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              <p>You do not have permission to access this page. Owner access required.</p>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await api.get('/auth/admin/users');
      setUsers(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const toggleLeagueAdmin = async (userId: string, currentValue: boolean) => {
    setError('');
    setSuccessMessage('');
    setProcessingUserId(userId);

    try {
      if (currentValue) {
        // Revoke league admin
        await api.patch(`/auth/admin/users/${userId}/revoke-league-admin`);
        setSuccessMessage('League admin revoked successfully');
      } else {
        // Grant league admin
        await api.patch(`/auth/admin/users/${userId}/grant-league-admin`);
        setSuccessMessage('League admin granted successfully');
      }
      await loadUsers();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update permissions');
    } finally {
      setProcessingUserId(null);
    }
  };

  const toggleOwner = async (userId: string, currentValue: boolean) => {
    setError('');
    setSuccessMessage('');
    setProcessingUserId(userId);

    try {
      if (currentValue) {
        // Revoke owner
        await api.patch(`/auth/admin/users/${userId}/revoke-owner`);
        setSuccessMessage('Owner revoked successfully');
      } else {
        // Grant owner
        await api.patch(`/auth/admin/users/${userId}/grant-owner`);
        setSuccessMessage('Owner granted successfully');
      }
      await loadUsers();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update permissions');
    } finally {
      setProcessingUserId(null);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Owner Portal</h1>
          <p className="text-gray-600 mb-6">Manage user permissions and access levels</p>

          <ErrorMessage message={error} />
          {successMessage && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
              <p>{successMessage}</p>
            </div>
          )}

          {loading ? (
            <LoadingSpinner />
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Joined
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Permissions
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {users.map((user) => {
                      const isCurrentUser = user.id === currentUser?.id;
                      const isProcessing = processingUserId === user.id;

                      return (
                        <tr key={user.id} className={isCurrentUser ? 'bg-blue-50' : ''}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="text-sm font-medium text-gray-900">
                                {user.username}
                                {isCurrentUser && (
                                  <span className="ml-2 text-xs text-blue-600">(You)</span>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-600">{user.email}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                            {format(new Date(user.created_at), 'MMM d, yyyy')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex flex-wrap gap-1">
                              {user.is_primary_owner && (
                                <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                                  Primary Owner
                                </span>
                              )}
                              {user.is_owner && !user.is_primary_owner && (
                                <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded">
                                  Owner
                                </span>
                              )}
                              {user.is_league_admin && !user.is_owner && (
                                <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">
                                  League Admin
                                </span>
                              )}
                              {!user.is_league_admin && !user.is_owner && (
                                <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded">
                                  User
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            {user.is_primary_owner ? (
                              <span className="text-gray-400 italic">Protected</span>
                            ) : isCurrentUser ? (
                              <span className="text-gray-400 italic">Cannot modify self</span>
                            ) : (
                              <div className="flex flex-col space-y-2">
                                {/* League Admin Toggle */}
                                <label className="flex items-center">
                                  <input
                                    type="checkbox"
                                    checked={user.is_league_admin}
                                    onChange={() => toggleLeagueAdmin(user.id, user.is_league_admin)}
                                    disabled={isProcessing}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
                                  />
                                  <span className="ml-2 text-gray-700">League Admin</span>
                                </label>

                                {/* Owner Toggle */}
                                <label className="flex items-center">
                                  <input
                                    type="checkbox"
                                    checked={user.is_owner}
                                    onChange={() => toggleOwner(user.id, user.is_owner)}
                                    disabled={isProcessing}
                                    className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded disabled:opacity-50"
                                  />
                                  <span className="ml-2 text-gray-700">Owner</span>
                                </label>
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {users.length === 0 && (
                <div className="px-6 py-4 text-center text-gray-500">No users found.</div>
              )}
            </div>
          )}

          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-900 mb-2">Permission Levels:</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>
                <strong>User</strong>: Can join leagues and draft players
              </li>
              <li>
                <strong>League Admin</strong>: User permissions + can create leagues
              </li>
              <li>
                <strong>Owner</strong>: League Admin permissions + can grant permissions and import
                tournaments
              </li>
              <li>
                <strong>Primary Owner</strong>: First user, all permissions, cannot be removed
              </li>
            </ul>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}

