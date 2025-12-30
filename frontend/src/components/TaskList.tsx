/**
 * TaskList Component
 * Displays list of tasks with empty state
 */

'use client';

import type { Task } from '@/types/task';
import { TaskItem } from './TaskItem';

interface TaskListProps {
  tasks: Task[];
  onToggle: (taskId: number) => void;
  onUpdate: (taskId: number, data: { title?: string; description?: string }) => void;
  onDelete: (taskId: number, taskTitle: string) => void;
  isLoading?: boolean;
}

export function TaskList({ tasks, onToggle, onUpdate, onDelete, isLoading = false }: TaskListProps) {
  // Empty state
  if (!isLoading && tasks.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-gray-300 bg-white p-12 text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
          />
        </svg>
        <h3 className="mt-2 text-sm font-semibold text-gray-900">No tasks yet</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by creating your first task above.
        </p>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-24 animate-pulse rounded-lg border border-gray-200 bg-gray-50"
          />
        ))}
      </div>
    );
  }

  // Task list
  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggle={onToggle}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
