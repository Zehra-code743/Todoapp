/**
 * TypeScript types and interfaces for Phase II Todo Application
 * Generated from: contracts/openapi.yaml
 * Date: 2025-12-26
 *
 * These types should be copied to frontend/src/types/ during implementation.
 */

// ============================================================================
// Core Data Models
// ============================================================================

/**
 * User entity (managed by Better Auth)
 */
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string; // ISO 8601 date-time
  updated_at: string; // ISO 8601 date-time
}

/**
 * Task entity (full representation from API)
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string; // ISO 8601 date-time
  updated_at: string; // ISO 8601 date-time
}

// ============================================================================
// API Request/Response Types
// ============================================================================

/**
 * Request body for creating a new task
 * POST /api/{user_id}/tasks
 */
export interface TaskCreateRequest {
  title: string; // 1-200 characters
  description?: string | null; // 0-1000 characters
}

/**
 * Request body for updating a task
 * PUT /api/{user_id}/tasks/{task_id}
 */
export interface TaskUpdateRequest {
  title?: string; // 1-200 characters
  description?: string | null; // 0-1000 characters
}

/**
 * Response for listing tasks
 * GET /api/{user_id}/tasks
 */
export interface TaskListResponse {
  tasks: Task[];
  count: number;
}

/**
 * Response for task deletion
 * DELETE /api/{user_id}/tasks/{task_id}
 */
export interface TaskDeleteResponse {
  message: string;
  task_id: number;
}

// ============================================================================
// API Error Types
// ============================================================================

/**
 * Generic error response
 */
export interface ApiError {
  detail: string;
}

/**
 * Validation error response (422 Unprocessable Entity)
 */
export interface ValidationError {
  detail: Array<{
    loc: string[]; // Field path, e.g., ["body", "title"]
    msg: string; // Error message
    type: string; // Error type, e.g., "value_error.any_str.min_length"
  }>;
}

// ============================================================================
// Query Parameters
// ============================================================================

/**
 * Query parameters for listing tasks
 * GET /api/{user_id}/tasks?status=...
 */
export type TaskStatus = 'all' | 'pending' | 'completed';

export interface TaskListQueryParams {
  status?: TaskStatus;
}

// ============================================================================
// Form Validation Types (Zod schemas)
// ============================================================================

/**
 * Validation constraints for task title
 */
export const TASK_TITLE_MIN_LENGTH = 1;
export const TASK_TITLE_MAX_LENGTH = 200;

/**
 * Validation constraints for task description
 */
export const TASK_DESCRIPTION_MAX_LENGTH = 1000;

/**
 * Validation constraints for user name
 */
export const USER_NAME_MIN_LENGTH = 2;
export const USER_NAME_MAX_LENGTH = 100;

/**
 * Validation constraints for password
 */
export const PASSWORD_MIN_LENGTH = 8;

// ============================================================================
// React Query Key Factories
// ============================================================================

/**
 * Query key factory for React Query
 * Ensures consistent cache keys across the application
 */
export const taskKeys = {
  all: ['tasks'] as const,
  lists: () => [...taskKeys.all, 'list'] as const,
  list: (userId: string, status?: TaskStatus) =>
    [...taskKeys.lists(), userId, status] as const,
  details: () => [...taskKeys.all, 'detail'] as const,
  detail: (userId: string, taskId: number) =>
    [...taskKeys.details(), userId, taskId] as const,
};

// ============================================================================
// API Client Configuration
// ============================================================================

/**
 * API client configuration
 */
export interface ApiClientConfig {
  baseURL: string;
  timeout?: number; // Request timeout in milliseconds
  getAuthToken: () => string | null; // Function to retrieve JWT token
  onUnauthorized?: () => void; // Callback for 401 errors (redirect to login)
}

// ============================================================================
// Helper Types
// ============================================================================

/**
 * Helper type for optimistic updates
 * Represents a task with pending server confirmation
 */
export interface OptimisticTask extends Task {
  _optimistic?: boolean; // Flag for optimistic updates
  _error?: string; // Error message if optimistic update failed
}

/**
 * Helper type for task form state
 */
export interface TaskFormData {
  title: string;
  description: string;
}

/**
 * Helper type for task filters
 */
export interface TaskFilters {
  status: TaskStatus;
  searchQuery?: string; // For future search functionality
}

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard to check if error is ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'detail' in error &&
    typeof (error as any).detail === 'string'
  );
}

/**
 * Type guard to check if error is ValidationError
 */
export function isValidationError(error: unknown): error is ValidationError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'detail' in error &&
    Array.isArray((error as any).detail)
  );
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Extract first error message from ValidationError
 */
export function getFirstValidationError(error: ValidationError): string {
  return error.detail[0]?.msg || 'Validation error';
}

/**
 * Format API error for display to user
 */
export function formatApiError(error: unknown): string {
  if (isApiError(error)) {
    return error.detail;
  }
  if (isValidationError(error)) {
    return getFirstValidationError(error);
  }
  return 'An unexpected error occurred';
}
