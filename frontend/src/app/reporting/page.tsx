'use client';

import React from 'react';
import { Globe, TrendingUp, CheckCircle, Clock } from 'lucide-react';

export default function TransparencyDashboard() {
  return (
    <div className="min-h-screen bg-[#050505] text-white selection:bg-blue-500/30">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-blue-600/5 blur-[120px] pointer-events-none"></div>
      
      <div className="max-w-7xl mx-auto px-6 py-12">
        <nav className="flex justify-between items-center mb-24 relative z-10">
          <div className="flex items-center gap-3">
            <Globe className="text-blue-500" />
            <span className="text-xl font-black tracking-tighter uppercase italic">Citiz_Eyes</span>
          </div>
          <div className="flex gap-8 text-sm font-medium text-slate-400">
            <a href="#" className="hover:text-blue-400 transition-colors">Real-time Map</a>
            <a href="#" className="hover:text-blue-400 transition-colors">Historical Data</a>
            <a href="#" className="hover:text-blue-400 transition-colors">Audit Logs</a>
          </div>
          <button className="bg-white text-black px-6 py-2 rounded-full font-bold text-sm hover:bg-blue-500 hover:text-white transition-all">
            Join Platform
          </button>
        </nav>

        <section className="mb-24 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 mb-8">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></div>
            <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Public Live Feed</span>
          </div>
          <h1 className="text-8xl font-black tracking-tight leading-[0.9] text-white">
            Absolute <br /> <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-800">Transparency.</span>
          </h1>
          <p className="max-w-xl mt-8 text-slate-400 text-lg leading-relaxed">
            Every report, every resolution, every penny accounted for. Building the future of civic trust through radical accountability and real-time reporting.
          </p>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative z-10">
          {[
            { label: 'Issues Resolved', val: '4,129', icon: CheckCircle, color: 'text-emerald-500' },
            { label: 'Active Reports', val: '243', icon: Globe, color: 'text-blue-500' },
            { label: 'Avg Solve Time', val: '18h', icon: Clock, color: 'text-amber-500' },
            { label: 'Public Confidence', val: '94%', icon: TrendingUp, color: 'text-indigo-500' },
          ].map((stat, i) => (
            <div key={i} className="bg-[#111] border border-white/5 p-8 rounded-[40px] group hover:border-white/10 transition-all hover:-translate-y-2">
              <stat.icon className={`${stat.color} mb-6`} size={32} />
              <p className="text-4xl font-black mb-1">{stat.val}</p>
              <p className="text-xs text-slate-500 font-mono uppercase tracking-widest">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Placeholder for Map */}
        <div className="mt-24 h-[500px] w-full bg-[#111] border border-white/5 rounded-[50px] relative overflow-hidden group shadow-2xl">
          <div className="absolute inset-0 flex items-center justify-center opacity-40">
            <span className="text-slate-800 font-black text-9xl italic">GEO_MAP_ACTIVE</span>
          </div>
          <div className="absolute top-8 left-8 p-6 bg-black/80 backdrop-blur-xl border border-white/10 rounded-3xl">
            <h3 className="font-bold text-lg mb-2">Issue Density</h3>
            <p className="text-xs text-slate-400">Current live resolution heatmap</p>
          </div>
          <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-60"></div>
          <div className="absolute bottom-12 left-1/2 -translate-x-1/2 bg-blue-600/20 backdrop-blur-xl border border-blue-500/30 px-8 py-4 rounded-full text-xs font-bold uppercase tracking-[0.2em] animate-bounce">
            Live Feed Scrolling...
          </div>
        </div>
      </div>
    </div>
  );
}
