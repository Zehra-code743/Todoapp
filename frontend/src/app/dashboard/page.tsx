/**
 * Dashboard Page
 * Main application page with task management (User Stories 2-5)
 */

'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import {
  useTasksQuery,
  useCreateTaskMutation,
  useUpdateTaskMutation,
  useToggleTaskMutation,
  useDeleteTaskMutation,
} from '@/hooks/useTasks';
import { TaskForm } from '@/components/TaskForm';
import { TaskList } from '@/components/TaskList';
import { DeleteConfirmDialog } from '@/components/DeleteConfirmDialog';
import { PlusCircle } from 'lucide-react';

export default function DashboardPage() {
  const { user, isLoading: authLoading } = useAuth();
  const userId = user?.id || '';

  // React Query hooks
  const { data: tasksData, isLoading: tasksLoading } = useTasksQuery(userId);
  const createMutation = useCreateTaskMutation(userId);
  const updateMutation = useUpdateTaskMutation(userId);
  const toggleMutation = useToggleTaskMutation(userId);
  const deleteMutation = useDeleteTaskMutation(userId);

  // Delete confirmation dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<{ id: number; title: string } | null>(null);

  if (authLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-solid border-current border-r-transparent">
            <span className="sr-only">Loading...</span>
          </div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  const tasks = tasksData?.tasks || [];
  const pendingCount = tasks.filter((t) => !t.completed).length;
  const completedCount = tasks.filter((t) => t.completed).length;
  const completionRate = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0;

  const handleCreateTask = async (data: { title: string; description?: string }) => {
    await createMutation.mutateAsync(data);
  };

  const handleToggleTask = (taskId: number) => {
    toggleMutation.mutate(taskId);
  };

  const handleUpdateTask = (taskId: number, data: { title?: string; description?: string }) => {
    updateMutation.mutate({ taskId, data });
  };

  const handleDeleteTask = (taskId: number, taskTitle: string) => {
    setTaskToDelete({ id: taskId, title: taskTitle });
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (taskToDelete) {
      await deleteMutation.mutateAsync(taskToDelete.id);
      setDeleteDialogOpen(false);
      setTaskToDelete(null);
    }
  };

  const handleCancelDelete = () => {
    setDeleteDialogOpen(false);
    setTaskToDelete(null);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-6 pb-2">
        <div>
          <h1 className="text-4xl font-black tracking-tighter text-foreground drop-shadow-sm">
            Control <span className="gradient-text">Center</span>
          </h1>
          <p className="text-muted-foreground font-medium mt-1">Operational overview of your active task sequences.</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex flex-col items-end">
            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground opacity-70">Efficiency</span>
            <span className="text-sm font-bold tabular-nums">
              {tasks.length > 0 ? (
                <span className="inline-flex items-center gap-2 text-primary">
                  <span className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse"></span>
                  {completionRate}% Nominal
                </span>
              ) : (
                'System Idle'
              )}
            </span>
          </div>
        </div>
      </div>

      {/* Task Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Tasks */}
        <div className="glass-card rounded-[2rem] p-6 group hover:translate-y-[-4px] transition-all duration-300">
          <div className="flex items-start justify-between">
            <div className="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-colors duration-500 shadow-inner">
              <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div className="text-[10px] font-black tracking-widest uppercase py-1 px-2.5 bg-muted rounded-full opacity-60">Total</div>
          </div>
          <div className="mt-6">
            <div className="text-4xl font-black tracking-tighter tabular-nums">{tasks.length}</div>
            <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mt-1 opacity-70">Indexed Tasks</p>
          </div>
        </div>

        {/* Pending Tasks */}
        <div className="glass-card rounded-[2rem] p-6 group hover:translate-y-[-4px] transition-all duration-300 border-l-amber-500/20">
          <div className="flex items-start justify-between">
            <div className="w-14 h-14 bg-amber-500/10 text-amber-600 rounded-2xl flex items-center justify-center group-hover:bg-amber-500 group-hover:text-white transition-colors duration-500 shadow-inner">
              <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="text-[10px] font-black tracking-widest uppercase py-1 px-2.5 bg-amber-500/10 text-amber-600 rounded-full">Active</div>
          </div>
          <div className="mt-6">
            <div className="text-4xl font-black tracking-tighter tabular-nums text-amber-600">{pendingCount}</div>
            <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mt-1 opacity-70">Processing</p>
          </div>
        </div>

        {/* Completed Tasks */}
        <div className="glass-card rounded-[2rem] p-6 group hover:translate-y-[-4px] transition-all duration-300 border-l-green-500/20">
          <div className="flex items-start justify-between">
            <div className="w-14 h-14 bg-green-500/10 text-green-600 rounded-2xl flex items-center justify-center group-hover:bg-green-500 group-hover:text-white transition-colors duration-500 shadow-inner">
              <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="text-[10px] font-black tracking-widest uppercase py-1 px-2.5 bg-green-500/10 text-green-600 rounded-full">Resolved</div>
          </div>
          <div className="mt-6">
            <div className="text-4xl font-black tracking-tighter tabular-nums text-green-600">{completedCount}</div>
            <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mt-1 opacity-70">Verified</p>
          </div>
        </div>

        {/* Progress */}
        <div className="glass-card rounded-[2rem] p-6 group hover:translate-y-[-4px] transition-all duration-300 border-l-indigo-500/20">
          <div className="flex items-start justify-between">
            <div className="w-14 h-14 bg-indigo-500/10 text-indigo-600 rounded-2xl flex items-center justify-center group-hover:bg-modern-gradient group-hover:text-white transition-all duration-500 shadow-inner ring-1 ring-primary/10">
              <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="text-[10px] font-black tracking-widest uppercase py-1 px-2.5 bg-indigo-500/10 text-indigo-600 rounded-full">Velocity</div>
          </div>
          <div className="mt-6">
            <div className="text-4xl font-black tracking-tighter tabular-nums gradient-text">{completionRate}%</div>
            <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mt-1 opacity-70">Network Load</p>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      {tasks.length > 0 && (
        <div className="glass-card rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-2 h-full bg-primary/20" />
          <div className="flex items-center justify-between mb-4 px-2">
            <span className="text-sm font-black uppercase tracking-widest text-foreground opacity-80">Global Synchronization</span>
            <span className="text-xs font-mono font-bold bg-muted px-2 py-1 rounded text-muted-foreground">{completedCount} / {tasks.length} SIGS</span>
          </div>
          <div className="h-4 bg-muted rounded-full p-1 overflow-hidden">
            <div
              className="h-full bg-modern-gradient rounded-full shadow-[0_0_15px_rgba(59,130,246,0.4)] transition-all duration-1000 ease-out"
              style={{ width: `${completionRate}%` }}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mt-4">
        {/* Create Task Form */}
        <div className="lg:col-span-5">
           <div className="glass-card rounded-[2.5rem] overflow-hidden shadow-premium h-full">
            <div className="px-8 py-6 border-b border-border/40 relative">
              <div className="absolute top-0 right-0 p-4 opacity-5">
                 <PlusCircle className="w-20 h-20" />
              </div>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-modern-gradient rounded-2xl flex items-center justify-center shadow-lg shadow-primary/20">
                  <PlusCircle className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-black tracking-tight text-foreground uppercase">New Protocol</h2>
                  <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest opacity-60">Register new active task</p>
                </div>
              </div>
            </div>
            <div className="p-8">
              <TaskForm onSubmit={handleCreateTask} isLoading={createMutation.isPending} />
            </div>
          </div>
        </div>

        {/* Task List */}
        <div className="lg:col-span-7">
          <div className="glass-card rounded-[2.5rem] overflow-hidden shadow-premium h-full">
            <div className="px-8 py-6 border-b border-border/40 bg-muted/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-background border border-border/60 rounded-2xl flex items-center justify-center shadow-sm">
                    <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 6h16M4 12h16M4 18h7" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-xl font-black tracking-tight text-foreground uppercase">Active Tasks</h2>
                    <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest opacity-60">Database query synchronized</p>
                  </div>
                </div>
                <div className="px-4 py-1.5 bg-background border border-border/60 rounded-full font-mono text-[10px] font-bold shadow-sm">
                   COUNT: {tasks.length}
                </div>
              </div>
            </div>
            <div className="p-4 lg:p-6 min-h-[400px]">
              <TaskList
                tasks={tasks}
                onToggle={handleToggleTask}
                onUpdate={handleUpdateTask}
                onDelete={handleDeleteTask}
                isLoading={tasksLoading}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        isOpen={deleteDialogOpen}
        taskTitle={taskToDelete?.title || ''}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        isDeleting={deleteMutation.isPending}
      />
    </div>
  );
}
