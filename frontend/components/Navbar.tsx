'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getUser, logout } from '@/lib/auth';
import { User } from '@/lib/api';

export default function Navbar() {
  const [user, setUser] = useState<User | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
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
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex justify-between items-center h-14">
          <div className="flex items-center space-x-8">
            <Link href="/dashboard" className="flex items-center">
              <span
                className="text-lg tracking-widest text-white"
                style={{ fontFamily: 'Georgia, serif', fontWeight: 400 }}
              >
                <span className="hidden sm:inline">GOLF </span>PICK&apos;EM
              </span>
            </Link>
            <div className="hidden md:flex items-center space-x-6">
              <Link
                href="/dashboard"
                className="text-white/80 hover:text-white text-sm tracking-wide transition-colors"
              >
                Leagues
              </Link>
              <Link
                href="/about"
                className="text-white/80 hover:text-white text-sm tracking-wide transition-colors"
              >
                About
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
          <div className="hidden md:flex items-center space-x-4">
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

          {/* Mobile hamburger */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden text-white p-1"
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {menuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile menu dropdown */}
        {menuOpen && (
          <div className="md:hidden pb-4 border-t border-white/10">
            <div className="pt-3 space-y-1">
              <Link
                href="/dashboard"
                onClick={() => setMenuOpen(false)}
                className="block py-2 text-white/80 hover:text-white text-sm tracking-wide"
              >
                Leagues
              </Link>
              <Link
                href="/about"
                onClick={() => setMenuOpen(false)}
                className="block py-2 text-white/80 hover:text-white text-sm tracking-wide"
              >
                About
              </Link>
              {user.is_owner && (
                <Link
                  href="/admin/users"
                  onClick={() => setMenuOpen(false)}
                  className="block py-2 text-white/80 hover:text-white text-sm tracking-wide"
                >
                  Admin
                </Link>
              )}
            </div>
            <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
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
              </div>
              <button
                onClick={handleLogout}
                className="text-white/60 hover:text-white text-sm transition-colors"
              >
                Sign Out
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
