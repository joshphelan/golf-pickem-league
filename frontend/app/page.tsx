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
    <div className="min-h-screen" style={{ background: '#fffef7' }}>
      {/* Hero */}
      <div
        style={{
          background: 'linear-gradient(135deg, #006747 0%, #004d35 100%)',
          borderBottom: '3px solid #c9a227',
        }}
      >
        <div className="max-w-4xl mx-auto px-6 py-20 text-center">
          <h1
            className="text-4xl md:text-5xl text-white mb-4"
            style={{ fontFamily: 'Georgia, serif', fontWeight: 400 }}
          >
            Golf Pick&apos;em League
          </h1>
          <p className="text-lg text-white/80 mb-10 max-w-xl mx-auto">
            Draft PGA Tour players, compete with friends, and track live tournament scores
          </p>

          <div className="flex justify-center gap-4">
            <Link
              href="/login"
              className="font-medium py-3 px-8 text-lg transition-opacity hover:opacity-90"
              style={{ background: '#c9a227', color: '#1a1a1a' }}
            >
              Login
            </Link>
            <Link
              href="/signup"
              className="font-medium py-3 px-8 text-lg transition-opacity hover:opacity-90"
              style={{ background: 'rgba(255,255,255,0.15)', color: 'white', border: '1px solid rgba(255,255,255,0.3)' }}
            >
              Sign Up
            </Link>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="max-w-4xl mx-auto px-6 py-16">
        <h2
          className="text-2xl text-center mb-10"
          style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}
        >
          How It Works
        </h2>

        <div className="grid md:grid-cols-4 gap-8 text-center mb-12">
          <div>
            <div
              className="w-10 h-10 mx-auto mb-3 flex items-center justify-center text-white text-sm font-semibold"
              style={{ background: '#006747', borderRadius: '50%' }}
            >
              1
            </div>
            <h3 className="font-medium mb-1" style={{ color: '#1a1a1a' }}>Create Account</h3>
            <p className="text-sm" style={{ color: '#666' }}>Sign up and get approved to join</p>
          </div>
          <div>
            <div
              className="w-10 h-10 mx-auto mb-3 flex items-center justify-center text-white text-sm font-semibold"
              style={{ background: '#006747', borderRadius: '50%' }}
            >
              2
            </div>
            <h3 className="font-medium mb-1" style={{ color: '#1a1a1a' }}>Join a League</h3>
            <p className="text-sm" style={{ color: '#666' }}>Create or join a league with an invite code</p>
          </div>
          <div>
            <div
              className="w-10 h-10 mx-auto mb-3 flex items-center justify-center text-white text-sm font-semibold"
              style={{ background: '#006747', borderRadius: '50%' }}
            >
              3
            </div>
            <h3 className="font-medium mb-1" style={{ color: '#1a1a1a' }}>Draft Players</h3>
            <p className="text-sm" style={{ color: '#666' }}>Pick your PGA Tour players before the deadline</p>
          </div>
          <div>
            <div
              className="w-10 h-10 mx-auto mb-3 flex items-center justify-center text-white text-sm font-semibold"
              style={{ background: '#006747', borderRadius: '50%' }}
            >
              4
            </div>
            <h3 className="font-medium mb-1" style={{ color: '#1a1a1a' }}>Compete</h3>
            <p className="text-sm" style={{ color: '#666' }}>Lowest combined score wins, just like real golf</p>
          </div>
        </div>

        <div className="text-center">
          <Link
            href="/about"
            className="text-sm font-medium transition-opacity hover:opacity-80"
            style={{ color: '#006747' }}
          >
            Learn more about Golf Pick&apos;em &rarr;
          </Link>
        </div>
      </div>
    </div>
  );
}
