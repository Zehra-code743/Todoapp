'use client';

import React from 'react';
import { ShieldCheck, MapPin, ClipboardList, Send } from 'lucide-react';

export default function CitizenPortal() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-600 mb-2">
            Citizen Reporting Portal
          </h1>
          <p className="text-slate-400">Welcome to the transparency platform. Report and track civic issues in your neighborhood.</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Report Issue Form Card */}
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-3xl p-8 shadow-2xl">
            <div className="flex items-center gap-3 mb-6 text-blue-400">
              <ClipboardList size={28} />
              <h2 className="text-2xl font-semibold text-white">Report New Issue</h2>
            </div>
            
            <form className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Issue Title</label>
                <input 
                  type="text" 
                  placeholder="e.g. Large pothole on Main St"
                  className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Category</label>
                <select className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                  <option>Roads & Infrastructure</option>
                  <option>Public Safety</option>
                  <option>Sanitation & Waste</option>
                  <option>Environment</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Description</label>
                <textarea 
                  rows={4}
                  placeholder="Provide details about the issue..."
                  className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                ></textarea>
              </div>

              <div className="flex gap-4 p-4 bg-slate-800/30 rounded-2xl border border-slate-700/50">
                <MapPin className="text-blue-400 shrink-0" />
                <div className="text-sm">
                  <p className="text-slate-200 font-medium">Detect Location</p>
                  <p className="text-slate-400">We'll use your current GPS coordinates.</p>
                </div>
                <button type="button" className="ml-auto text-blue-400 text-sm hover:underline">Pick on map</button>
              </div>

              <button className="w-full bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-500 hover:to-indigo-600 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-900/20 transition-all flex items-center justify-center gap-2">
                <Send size={20} />
                Submit Report
              </button>
            </form>
          </div>

          {/* Status Tracker */}
          <div className="space-y-8">
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-3xl p-8 shadow-2xl">
              <div className="flex items-center gap-3 mb-6 text-indigo-400">
                <ShieldCheck size={28} />
                <h2 className="text-2xl font-semibold text-white">My Active Reports</h2>
              </div>
              
              <div className="space-y-4">
                {[1, 2].map((i) => (
                  <div key={i} className="p-4 bg-slate-800/50 rounded-2xl border border-slate-700/50 flex justify-between items-center group hover:border-slate-600 transition-all cursor-pointer">
                    <div>
                      <h3 className="font-medium text-white group-hover:text-blue-400 transition-colors">Street light broken #00{i}</h3>
                      <p className="text-xs text-slate-400 mt-1">Submitted 2 days ago • Roads</p>
                    </div>
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                      In Progress
                    </span>
                  </div>
                ))}
              </div>
              
              <button className="w-full mt-6 text-center text-slate-400 hover:text-white text-sm transition-colors">
                View all report history
              </button>
            </div>
            
            {/* Quick Stats Summary */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-600/10 border border-blue-500/20 rounded-3xl p-6 text-center">
                <p className="text-4xl font-bold text-blue-400">12</p>
                <p className="text-sm text-slate-400 mt-1">Resolved issues</p>
              </div>
              <div className="bg-indigo-600/10 border border-indigo-500/20 rounded-3xl p-6 text-center">
                <p className="text-4xl font-bold text-indigo-400">98%</p>
                <p className="text-sm text-slate-400 mt-1">Civic rating</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
