/**
 * useTasks Hooks
 * React Query hooks for task CRUD operations with optimistic updates
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type {
  Task,
  TaskCreateRequest,
  TaskUpdateRequest,
  TaskListResponse,
  taskKeys,
} from '@/types/task';

/**
 * Query key factory for consistent cache management
 */
export const TASK_KEYS = {
  all: ['tasks'] as const,
  lists: () => [...TASK_KEYS.all, 'list'] as const,
  list: (userId: string, status?: 'all' | 'pending' | 'completed') =>
    [...TASK_KEYS.lists(), userId, status] as const,
};

/**
 * Hook to fetch tasks for a user
 */
export function useTasksQuery(userId: string, status?: 'all' | 'pending' | 'completed') {
  return useQuery({
    queryKey: TASK_KEYS.list(userId, status),
    queryFn: () => apiClient.getTasks(userId, status),
    enabled: !!userId,
  });
}

/**
 * Hook to create a new task with optimistic update
 */
export function useCreateTaskMutation(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TaskCreateRequest) => apiClient.createTask(userId, data),
    onMutate: async (newTask) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: TASK_KEYS.list(userId) });

      // Snapshot previous value
      const previousTasks = queryClient.getQueryData<TaskListResponse>(
        TASK_KEYS.list(userId)
      );

      // Optimistically update cache
      if (previousTasks) {
        const optimisticTask: Task = {
          id: Date.now(), // Temporary ID
          user_id: userId,
          title: newTask.title,
          description: newTask.description || null,
          completed: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };

        queryClient.setQueryData<TaskListResponse>(TASK_KEYS.list(userId), {
          tasks: [optimisticTask, ...previousTasks.tasks],
          count: previousTasks.count + 1,
        });
      }

      return { previousTasks };
    },
    onError: (err, newTask, context) => {
      // Rollback on error
      if (context?.previousTasks) {
        queryClient.setQueryData(TASK_KEYS.list(userId), context.previousTasks);
      }
    },
    onSettled: () => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.list(userId) });
    },
  });
}

/**
 * Hook to update a task with optimistic update
 */
export function useUpdateTaskMutation(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, data }: { taskId: number; data: TaskUpdateRequest }) =>
      apiClient.updateTask(userId, taskId, data),
    onMutate: async ({ taskId, data }) => {
      await queryClient.cancelQueries({ queryKey: TASK_KEYS.list(userId) });

      const previousTasks = queryClient.getQueryData<TaskListResponse>(
        TASK_KEYS.list(userId)
      );

      if (previousTasks) {
        queryClient.setQueryData<TaskListResponse>(TASK_KEYS.list(userId), {
          tasks: previousTasks.tasks.map((task) =>
            task.id === taskId
              ? { ...task, ...data, updated_at: new Date().toISOString() }
              : task
          ),
          count: previousTasks.count,
        });
      }

      return { previousTasks };
    },
    onError: (err, variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(TASK_KEYS.list(userId), context.previousTasks);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.list(userId) });
    },
  });
}

/**
 * Hook to toggle task completion with optimistic update
 */
export function useToggleTaskMutation(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: number) => apiClient.toggleTaskCompletion(userId, taskId),
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: TASK_KEYS.list(userId) });

      const previousTasks = queryClient.getQueryData<TaskListResponse>(
        TASK_KEYS.list(userId)
      );

      if (previousTasks) {
        queryClient.setQueryData<TaskListResponse>(TASK_KEYS.list(userId), {
          tasks: previousTasks.tasks.map((task) =>
            task.id === taskId
              ? { ...task, completed: !task.completed, updated_at: new Date().toISOString() }
              : task
          ),
          count: previousTasks.count,
        });
      }

      return { previousTasks };
    },
    onError: (err, taskId, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(TASK_KEYS.list(userId), context.previousTasks);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.list(userId) });
    },
  });
}

/**
 * Hook to delete a task with optimistic update
 */
export function useDeleteTaskMutation(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: number) => apiClient.deleteTask(userId, taskId),
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: TASK_KEYS.list(userId) });

      const previousTasks = queryClient.getQueryData<TaskListResponse>(
        TASK_KEYS.list(userId)
      );

      if (previousTasks) {
        queryClient.setQueryData<TaskListResponse>(TASK_KEYS.list(userId), {
          tasks: previousTasks.tasks.filter((task) => task.id !== taskId),
          count: previousTasks.count - 1,
        });
      }

      return { previousTasks };
    },
    onError: (err, taskId, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(TASK_KEYS.list(userId), context.previousTasks);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.list(userId) });
    },
  });
}
