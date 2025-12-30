/**
 * TaskForm Component
 * Form for creating new tasks with validation
 */

'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { TASK_TITLE_MIN_LENGTH, TASK_TITLE_MAX_LENGTH, TASK_DESCRIPTION_MAX_LENGTH } from '@/types/task';

interface TaskFormProps {
  onSubmit: (data: { title: string; description?: string }) => Promise<void>;
  isLoading?: boolean;
}

export function TaskForm({ onSubmit, isLoading = false }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!title || title.trim().length === 0) {
      setError('Title is required');
      return;
    }

    if (title.length < TASK_TITLE_MIN_LENGTH || title.length > TASK_TITLE_MAX_LENGTH) {
      setError(`Title must be between ${TASK_TITLE_MIN_LENGTH} and ${TASK_TITLE_MAX_LENGTH} characters`);
      return;
    }

    if (description && description.length > TASK_DESCRIPTION_MAX_LENGTH) {
      setError(`Description must not exceed ${TASK_DESCRIPTION_MAX_LENGTH} characters`);
      return;
    }

    try {
      console.log('Submitting task:', { title: title.trim(), description: description.trim() || undefined });
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
      });
      console.log('Task created successfully');
      // Clear form on success
      setTitle('');
      setDescription('');
    } catch (err) {
      console.error('Task creation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to create task');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md bg-red-50 p-3">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div>
        <Label htmlFor="title">Task Title *</Label>
        <Input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter task title"
          maxLength={TASK_TITLE_MAX_LENGTH}
          required
          disabled={isLoading}
        />
        <p className="mt-1 text-xs text-gray-500">
          {title.length}/{TASK_TITLE_MAX_LENGTH} characters
        </p>
      </div>

      <div>
        <Label htmlFor="description">Description (optional)</Label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add optional description"
          maxLength={TASK_DESCRIPTION_MAX_LENGTH}
          rows={3}
          disabled={isLoading}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:cursor-not-allowed disabled:opacity-50"
        />
        <p className="mt-1 text-xs text-gray-500">
          {description.length}/{TASK_DESCRIPTION_MAX_LENGTH} characters
        </p>
      </div>

      <Button type="submit" disabled={isLoading || !title.trim()} className="w-full">
        {isLoading ? 'Creating...' : 'Create Task'}
      </Button>
    </form>
  );
}
