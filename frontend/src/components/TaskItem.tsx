/**
 * TaskItem Component
 * Individual task display with checkbox, edit, and delete actions
 */

'use client';

import { useState } from 'react';
import type { Task } from '@/types/task';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { TASK_TITLE_MAX_LENGTH, TASK_DESCRIPTION_MAX_LENGTH } from '@/types/task';
import { formatDate } from '@/lib/utils';

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: number) => void;
  onUpdate: (taskId: number, data: { title?: string; description?: string }) => void;
  onDelete: (taskId: number, taskTitle: string) => void;
  isUpdating?: boolean;
  isToggling?: boolean;
  isDeleting?: boolean;
}

export function TaskItem({
  task,
  onToggle,
  onUpdate,
  onDelete,
  isUpdating = false,
  isToggling = false,
  isDeleting = false,
}: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [error, setError] = useState('');

  const handleSave = () => {
    setError('');

    // Validation
    if (!editTitle.trim()) {
      setError('Title cannot be empty');
      return;
    }

    if (editTitle.length > TASK_TITLE_MAX_LENGTH) {
      setError(`Title must not exceed ${TASK_TITLE_MAX_LENGTH} characters`);
      return;
    }

    if (editDescription.length > TASK_DESCRIPTION_MAX_LENGTH) {
      setError(`Description must not exceed ${TASK_DESCRIPTION_MAX_LENGTH} characters`);
      return;
    }

    onUpdate(task.id, {
      title: editTitle.trim(),
      description: editDescription.trim() || undefined,
    });

    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setError('');
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  if (isEditing) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        {error && (
          <div className="mb-3 rounded-md bg-red-50 p-2">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="space-y-3">
          <div>
            <Input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={handleKeyDown}
              maxLength={TASK_TITLE_MAX_LENGTH}
              placeholder="Task title"
              disabled={isUpdating}
              autoFocus
            />
            <p className="mt-1 text-xs text-gray-500">
              {editTitle.length}/{TASK_TITLE_MAX_LENGTH}
            </p>
          </div>

          <div>
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              onKeyDown={handleKeyDown}
              maxLength={TASK_DESCRIPTION_MAX_LENGTH}
              placeholder="Description (optional)"
              rows={3}
              disabled={isUpdating}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:cursor-not-allowed disabled:opacity-50"
            />
            <p className="mt-1 text-xs text-gray-500">
              {editDescription.length}/{TASK_DESCRIPTION_MAX_LENGTH}
            </p>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleSave} disabled={isUpdating} size="sm">
              {isUpdating ? 'Saving...' : 'Save'}
            </Button>
            <Button onClick={handleCancel} disabled={isUpdating} variant="outline" size="sm">
              Cancel
            </Button>
          </div>

          <p className="text-xs text-gray-500">
            Press Enter to save, Escape to cancel
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="group rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md">
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => onToggle(task.id)}
          disabled={isToggling}
          className="mt-1 h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary disabled:cursor-not-allowed disabled:opacity-50"
          aria-label={task.completed ? 'Mark as pending' : 'Mark as completed'}
        />

        {/* Task Content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-base font-medium ${
              task.completed
                ? 'text-gray-400 line-through'
                : 'text-gray-900'
            } transition-all duration-200`}
          >
            {task.title}
          </h3>

          {task.description && (
            <p
              className={`mt-1 text-sm ${
                task.completed ? 'text-gray-400' : 'text-gray-600'
              }`}
            >
              {task.description}
            </p>
          )}

          <p className="mt-2 text-xs text-gray-500">
            Created {formatDate(task.created_at)}
            {task.updated_at !== task.created_at && ` • Updated ${formatDate(task.updated_at)}`}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            onClick={() => setIsEditing(true)}
            variant="outline"
            size="sm"
            disabled={isUpdating || isDeleting}
          >
            Edit
          </Button>
          <Button
            onClick={() => onDelete(task.id, task.title)}
            variant="outline"
            size="sm"
            disabled={isUpdating || isDeleting}
            className="text-red-600 hover:bg-red-50 hover:text-red-700"
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
}
