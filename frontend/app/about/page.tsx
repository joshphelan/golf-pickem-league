'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { isAuthenticated } from '@/lib/auth';

export default function AboutPage() {
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setAuthed(isAuthenticated());
  }, []);

  return (
    <div className="min-h-screen" style={{ background: '#fffef7' }}>
      {/* Header */}
      <div
        style={{
          background: 'linear-gradient(135deg, #006747 0%, #004d35 100%)',
          borderBottom: '3px solid #c9a227',
        }}
      >
        <div className="max-w-3xl mx-auto px-6 py-12 text-center">
          <h1
            className="text-3xl md:text-4xl text-white mb-3"
            style={{ fontFamily: 'Georgia, serif', fontWeight: 400 }}
          >
            About Golf Pick&apos;em
          </h1>
          <p className="text-white/80">Everything you need to know about how it works</p>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-12 space-y-12">
        {/* What Is It */}
        <section>
          <h2 className="text-xl mb-3" style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}>
            What is Golf Pick&apos;em?
          </h2>
          <p style={{ color: '#444', lineHeight: 1.7 }}>
            Golf Pick&apos;em is a fantasy golf league platform where you draft real PGA Tour players
            and compete against friends. Each week, pick your team for the upcoming tournament and see
            who comes out on top based on actual tournament scores.
          </p>
        </section>

        {/* How It Works */}
        <section>
          <h2 className="text-xl mb-4" style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}>
            How It Works
          </h2>
          <div className="space-y-4">
            {[
              { step: '1', title: 'Create an Account', desc: 'Sign up with your email. An admin will approve your account so you can start playing.' },
              { step: '2', title: 'Create or Join a League', desc: 'Start your own league for a specific PGA Tour tournament, or join an existing one using an invite code from a friend.' },
              { step: '3', title: 'Draft Your Players', desc: 'Before the draft deadline, pick your team of PGA Tour players from the tournament field. Each player can only be drafted by one team in the league.' },
              { step: '4', title: 'Track Live Scores', desc: 'Once the tournament begins, scores update automatically throughout the day. Watch the leaderboard to see how your team stacks up.' },
              { step: '5', title: 'Lowest Score Wins', desc: 'Just like real golf, the team with the lowest combined score at the end of the tournament wins the league.' },
            ].map((item) => (
              <div key={item.step} className="flex gap-4 items-start">
                <div
                  className="w-8 h-8 flex-shrink-0 flex items-center justify-center text-white text-sm font-semibold"
                  style={{ background: '#006747', borderRadius: '50%' }}
                >
                  {item.step}
                </div>
                <div>
                  <h3 className="font-medium" style={{ color: '#1a1a1a' }}>{item.title}</h3>
                  <p className="text-sm mt-0.5" style={{ color: '#666' }}>{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Scoring */}
        <section>
          <h2 className="text-xl mb-3" style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}>
            Scoring
          </h2>
          <p style={{ color: '#444', lineHeight: 1.7 }}>
            Your team score is the sum of all your drafted players&apos; total tournament scores.
            Scores are relative to par &mdash; a player at -5 contributes -5 to your team total.
            The team with the lowest total score wins the league, just like in real golf.
          </p>
        </section>

        {/* Live Updates */}
        <section>
          <h2 className="text-xl mb-3" style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}>
            Live Updates
          </h2>
          <p style={{ color: '#444', lineHeight: 1.7 }}>
            During active tournaments, scores are synced automatically every few minutes during
            playing hours. You can check the league leaderboard anytime to see current standings
            and individual player scores.
          </p>
        </section>

        {/* Data Source */}
        <section>
          <h2 className="text-xl mb-3" style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}>
            Data
          </h2>
          <p style={{ color: '#444', lineHeight: 1.7 }}>
            Tournament schedules, player fields, and live scores are powered by the Live Golf Data API,
            providing real-time PGA Tour data.
          </p>
        </section>

        {/* CTA */}
        <section
          className="text-center py-8 px-6"
          style={{ background: 'white', border: '1px solid #e5e2d3' }}
        >
          <h2 className="text-xl mb-4" style={{ fontFamily: 'Georgia, serif', color: '#1a1a1a' }}>
            Ready to Play?
          </h2>
          {authed ? (
            <Link
              href="/dashboard"
              className="inline-block font-medium py-3 px-8 text-white transition-opacity hover:opacity-90"
              style={{ background: '#006747' }}
            >
              Go to Dashboard
            </Link>
          ) : (
            <div className="flex justify-center gap-4">
              <Link
                href="/signup"
                className="inline-block font-medium py-3 px-8 text-white transition-opacity hover:opacity-90"
                style={{ background: '#006747' }}
              >
                Sign Up
              </Link>
              <Link
                href="/login"
                className="inline-block font-medium py-3 px-8 transition-opacity hover:opacity-90"
                style={{ background: '#c9a227', color: '#1a1a1a' }}
              >
                Login
              </Link>
            </div>
          )}
        </section>

        {/* Back link */}
        <div className="text-center">
          <Link href="/" className="text-sm hover:underline" style={{ color: '#006747' }}>
            &larr; Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
