/**
 * TaskForm Component
 * Form for creating new tasks with validation
 */

'use client';

import { useState } from 'react';
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
    <form onSubmit={handleSubmit} className="space-y-5">
      {error && (
        <div className="rounded-lg bg-red-50 border border-red-100 p-4">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
          Task Title <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What needs to be done?"
            maxLength={TASK_TITLE_MAX_LENGTH}
            required
            disabled={isLoading}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50 text-gray-900 placeholder-gray-400"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <span className={`text-xs font-medium ${
              title.length > TASK_TITLE_MAX_LENGTH * 0.9
                ? 'text-red-500'
                : title.length > TASK_TITLE_MAX_LENGTH * 0.7
                  ? 'text-amber-500'
                  : 'text-gray-400'
            }`}>
              {title.length}/{TASK_TITLE_MAX_LENGTH}
            </span>
          </div>
        </div>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
          Description <span className="text-gray-400 font-normal">(optional)</span>
        </label>
        <div className="relative">
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add more details about this task..."
            maxLength={TASK_DESCRIPTION_MAX_LENGTH}
            rows={4}
            disabled={isLoading}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50 resize-none text-gray-900 placeholder-gray-400"
          />
          <div className="absolute bottom-3 right-3">
            <span className={`text-xs font-medium ${
              description.length > TASK_DESCRIPTION_MAX_LENGTH * 0.9
                ? 'text-red-500'
                : description.length > TASK_DESCRIPTION_MAX_LENGTH * 0.7
                  ? 'text-amber-500'
                  : 'text-gray-400'
            }`}>
              {description.length}/{TASK_DESCRIPTION_MAX_LENGTH}
            </span>
          </div>
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading || !title.trim()}
        className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-300 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40"
      >
        {isLoading ? (
          <>
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-r-transparent"></div>
            <span>Creating...</span>
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Create Task</span>
          </>
        )}
      </button>
    </form>
  );
}
