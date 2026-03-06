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
    <div className="min-h-screen bg-[var(--cream)]">
      {/* Hero */}
      <div className="bg-gradient-to-br from-[var(--masters-green)] to-[var(--masters-green-dark)] border-b-[3px] border-[var(--masters-gold)]">
        <div className="max-w-4xl mx-auto px-6 py-24 text-center">
          <h1 className="text-4xl md:text-5xl text-white mb-4 font-display font-normal tracking-wide">
            Golf Pick&apos;em League
          </h1>
          <p className="text-lg text-white/80 mb-12 max-w-xl mx-auto">
            Draft PGA Tour players, compete with friends, and track live tournament scores
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              href="/login"
              className="font-medium py-3 px-8 text-lg rounded-lg bg-[var(--masters-gold)] text-[var(--charcoal)] transition-all hover:brightness-110 hover:shadow-lg text-center"
            >
              Login
            </Link>
            <Link
              href="/signup"
              className="font-medium py-3 px-8 text-lg rounded-lg bg-white/15 text-white border border-white/30 transition-all hover:bg-white/25 hover:shadow-lg text-center backdrop-blur-sm"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="max-w-4xl mx-auto px-6 py-20">
        <h2 className="text-2xl text-center mb-12 font-display text-[var(--charcoal)]">
          How It Works
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-14">
          {[
            { num: '1', title: 'Create Account', desc: 'Sign up and get approved to join' },
            { num: '2', title: 'Join a League', desc: 'Create or join a league with an invite code' },
            { num: '3', title: 'Draft Players', desc: 'Pick your PGA Tour players before the deadline' },
            { num: '4', title: 'Compete', desc: 'Lowest combined score wins, just like real golf' },
          ].map((step) => (
            <div
              key={step.num}
              className="text-center bg-white rounded-xl p-6 shadow-sm card-hover"
            >
              <div className="w-10 h-10 mx-auto mb-4 flex items-center justify-center text-white text-sm font-semibold rounded-full bg-[var(--masters-green)]">
                {step.num}
              </div>
              <h3 className="font-medium mb-1 text-[var(--charcoal)]">{step.title}</h3>
              <p className="text-sm text-gray-500">{step.desc}</p>
            </div>
          ))}
        </div>

        <div className="text-center">
          <Link
            href="/about"
            className="text-sm font-medium text-[var(--masters-green)] transition-colors hover:text-[var(--masters-green-dark)]"
          >
            Learn more about Golf Pick&apos;em &rarr;
          </Link>
        </div>
      </div>
    </div>
  );
}
