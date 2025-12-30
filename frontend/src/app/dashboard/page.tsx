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
import { Card } from '@/components/ui/Card';

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
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent">
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
      {/* Task Statistics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card className="p-4">
          <p className="text-sm text-gray-600">Total Tasks</p>
          <p className="mt-1 text-3xl font-bold text-gray-900">{tasks.length}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-600">Pending</p>
          <p className="mt-1 text-3xl font-bold text-yellow-600">{pendingCount}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-600">Completed</p>
          <p className="mt-1 text-3xl font-bold text-green-600">{completedCount}</p>
        </Card>
      </div>

      {/* Create Task Form */}
      <Card className="p-6">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Create New Task</h2>
        <TaskForm onSubmit={handleCreateTask} isLoading={createMutation.isPending} />
      </Card>

      {/* Task List */}
      <div>
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Your Tasks</h2>
        <TaskList
          tasks={tasks}
          onToggle={handleToggleTask}
          onUpdate={handleUpdateTask}
          onDelete={handleDeleteTask}
          isLoading={tasksLoading}
        />
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
