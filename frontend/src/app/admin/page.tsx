'use client';

import React from 'react';
import { LayoutDashboard, Users, FileText, BarChart, Settings, Bell } from 'lucide-react';

export default function AdminDashboard() {
  return (
    <div className="min-h-screen bg-slate-950 flex text-slate-100">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900/80 border-r border-slate-800 p-6 flex flex-col gap-8">
        <div className="flex items-center gap-2 mb-4">
          <LayoutDashboard className="text-blue-500" />
          <span className="font-bold text-xl tracking-tight">CITIZEN ADMIN</span>
        </div>
        
        <nav className="flex flex-col gap-2">
          <button className="flex items-center gap-3 px-4 py-3 rounded-xl bg-blue-600/10 text-blue-400 font-medium">
            <LayoutDashboard size={20} /> Dashboard
          </button>
          <button className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 transition-colors">
            <FileText size={20} /> Reports
          </button>
          <button className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 transition-colors">
            <Users size={20} /> Departments
          </button>
          <button className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 transition-colors">
            <BarChart size={20} /> Analytics
          </button>
          <button className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 transition-colors">
            <Settings size={20} /> Settings
          </button>
        </nav>

        <div className="mt-auto p-4 bg-gradient-to-br from-indigo-900/30 to-blue-900/10 rounded-2xl border border-indigo-500/20">
          <p className="text-xs text-slate-400 mb-2 font-mono uppercase tracking-widest">System Status</p>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span className="text-sm font-medium">Server Online</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <header className="flex justify-between items-center mb-12">
          <div>
            <h1 className="text-3xl font-bold text-white">Administration Hub</h1>
            <p className="text-slate-400 mt-1">Manage system configurations and review reporting data.</p>
          </div>
          <div className="flex gap-4">
            <button className="w-10 h-10 flex items-center justify-center rounded-full bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors">
              <Bell size={20} />
            </button>
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600"></div>
          </div>
        </header>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Reports Table */}
          <div className="lg:col-span-2 bg-slate-900/50 rounded-3xl border border-slate-800 p-8 shadow-xl">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-white">Pending Reports</h2>
              <button className="text-sm text-blue-400 hover:underline">View All</button>
            </div>
            
            <table className="w-full">
              <thead>
                <tr className="text-left text-slate-500 text-sm border-b border-slate-800">
                  <th className="pb-4 font-medium italic">Issue Description</th>
                  <th className="pb-4 font-medium italic">Category</th>
                  <th className="pb-4 font-medium italic">Assignee</th>
                  <th className="pb-4 font-medium italic text-right">Action</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {[1, 2, 3].map((i) => (
                  <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                    <td className="py-4">
                      <p className="font-medium text-slate-200">Water leakage - sector 5</p>
                      <p className="text-xs text-slate-500">2h ago</p>
                    </td>
                    <td className="py-4">
                      <span className="px-2 py-1 rounded-md bg-blue-500/10 text-blue-400 text-xs uppercase tracking-tighter">Utility</span>
                    </td>
                    <td className="py-4 text-slate-400 italic font-mono">Dept_Infrastructure</td>
                    <td className="py-4 text-right">
                      <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-100 transition-all font-bold">Review</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Rapid Stats */}
          <div className="space-y-6">
            <div className="bg-slate-900/50 rounded-3xl border border-slate-800 p-8 shadow-xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-6 opacity-10 blur-xl scale-150 group-hover:scale-125 transition-transform">
                <BarChart size={120} className="text-blue-500" />
              </div>
              <p className="text-sm text-slate-400 font-mono italic">Average Response Time</p>
              <p className="text-5xl font-black text-white mt-1">4.2h</p>
              <div className="flex items-center gap-2 mt-4 text-emerald-400 text-xs">
                <span>↑ 12% from last week</span>
              </div>
            </div>

            <div className="bg-slate-900/50 rounded-3xl border border-slate-800 p-8 shadow-xl">
              <h3 className="text-lg font-semibold text-white mb-6">Department Health</h3>
              <div className="space-y-4">
                {['Infrastructure', 'Sanitation', 'Safety'].map((dept) => (
                  <div key={dept}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-400">{dept}</span>
                      <span className="text-slate-100">85%</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 w-[85%]"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
