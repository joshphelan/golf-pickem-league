'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { isAuthenticated } from '@/lib/auth';
import Navbar from '@/components/Navbar';

export default function AboutPage() {
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setAuthed(isAuthenticated());
  }, []);

  return (
    <div className="min-h-screen bg-[var(--cream)]">
      <Navbar />
      {/* Header */}
      <div className="bg-gradient-to-br from-[var(--masters-green)] to-[var(--masters-green-dark)] border-b-[3px] border-[var(--masters-gold)]">
        <div className="max-w-3xl mx-auto px-6 py-14 text-center">
          <h1 className="text-3xl md:text-4xl text-white mb-3 font-display font-normal">
            About Golf Pick&apos;em
          </h1>
          <p className="text-white/80">Everything you need to know about how it works</p>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-14 space-y-12">
        {/* What Is It */}
        <section>
          <h2 className="text-xl mb-3 font-display text-[var(--charcoal)]">
            What is Golf Pick&apos;em?
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Golf Pick&apos;em is a fantasy golf league platform where you draft real PGA Tour players
            and compete against friends. Each week, pick your team for the upcoming tournament and see
            who comes out on top based on actual tournament scores.
          </p>
        </section>

        {/* How It Works */}
        <section>
          <h2 className="text-xl mb-5 font-display text-[var(--charcoal)]">
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
              <div key={item.step} className="flex gap-4 items-start bg-white rounded-xl p-4 shadow-sm">
                <div className="w-8 h-8 flex-shrink-0 flex items-center justify-center text-white text-sm font-semibold rounded-full bg-[var(--masters-green)]">
                  {item.step}
                </div>
                <div>
                  <h3 className="font-medium text-[var(--charcoal)]">{item.title}</h3>
                  <p className="text-sm mt-0.5 text-gray-500">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Scoring */}
        <section>
          <h2 className="text-xl mb-3 font-display text-[var(--charcoal)]">
            Scoring
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Your team score is the sum of all your drafted players&apos; total tournament scores.
            Scores are relative to par &mdash; a player at -5 contributes -5 to your team total.
            The team with the lowest total score wins the league, just like in real golf.
          </p>
        </section>

        {/* Live Updates */}
        <section>
          <h2 className="text-xl mb-3 font-display text-[var(--charcoal)]">
            Live Updates
          </h2>
          <p className="text-gray-600 leading-relaxed">
            During active tournaments, scores are synced automatically every few minutes during
            playing hours. You can check the league leaderboard anytime to see current standings
            and individual player scores.
          </p>
        </section>

        {/* Data Source */}
        <section>
          <h2 className="text-xl mb-3 font-display text-[var(--charcoal)]">
            Data
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Tournament schedules, player fields, and live scores are powered by the Live Golf Data API,
            providing real-time PGA Tour data.
          </p>
        </section>

        {/* CTA */}
        <section className="text-center py-10 px-6 bg-white rounded-xl shadow-sm border border-[#e5e2d3]">
          <h2 className="text-xl mb-5 font-display text-[var(--charcoal)]">
            Ready to Play?
          </h2>
          {authed ? (
            <Link
              href="/dashboard"
              className="inline-block font-medium py-3 px-8 rounded-lg text-white bg-[var(--masters-green)] transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-md"
            >
              Go to Dashboard
            </Link>
          ) : (
            <div className="flex justify-center gap-4">
              <Link
                href="/signup"
                className="inline-block font-medium py-3 px-8 rounded-lg text-white bg-[var(--masters-green)] transition-all hover:bg-[var(--masters-green-dark)] hover:shadow-md"
              >
                Sign Up
              </Link>
              <Link
                href="/login"
                className="inline-block font-medium py-3 px-8 rounded-lg bg-[var(--masters-gold)] text-[var(--charcoal)] transition-all hover:brightness-110 hover:shadow-md"
              >
                Login
              </Link>
            </div>
          )}
        </section>

        {/* Back link */}
        <div className="text-center">
          <Link href="/" className="text-sm text-[var(--masters-green)] hover:underline">
            &larr; Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
