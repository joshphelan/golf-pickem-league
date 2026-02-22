'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getUser, logout } from '@/lib/auth';
import { User } from '@/lib/api';

export default function Navbar() {
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();

  useEffect(() => {
    setUser(getUser());
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (!user) return null;

  return (
    <nav className="masters-header">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex justify-between items-center h-14">
          <div className="flex items-center space-x-8">
            <Link href="/dashboard" className="flex items-center">
              <span
                className="text-lg tracking-widest text-white"
                style={{ fontFamily: 'Georgia, serif', fontWeight: 400 }}
              >
                GOLF PICK&apos;EM
              </span>
            </Link>
            <div className="flex items-center space-x-6">
              <Link
                href="/dashboard"
                className="text-white/80 hover:text-white text-sm tracking-wide transition-colors"
              >
                Leagues
              </Link>
              {user.is_owner && (
                <Link
                  href="/admin/users"
                  className="text-white/80 hover:text-white text-sm tracking-wide transition-colors"
                >
                  Admin
                </Link>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-white/70 text-sm">{user.username}</span>
            {user.is_owner && (
              <span
                className="px-2 py-0.5 text-xs tracking-wide"
                style={{ background: '#c9a227', color: '#1a1a1a' }}
              >
                OWNER
              </span>
            )}
            {user.is_league_admin && !user.is_owner && (
              <span
                className="px-2 py-0.5 text-xs tracking-wide"
                style={{ background: '#c9a227', color: '#1a1a1a' }}
              >
                ADMIN
              </span>
            )}
            <button
              onClick={handleLogout}
              className="text-white/60 hover:text-white text-sm transition-colors"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
