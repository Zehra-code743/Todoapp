/**
 * Task Display Component
 * Displays task information with enhanced features (priority, tags, due dates)
 */

import React from 'react';
import './task-display.css'; // We'll create this CSS file too

interface TaskProps {
  id: number;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  priority: 'high' | 'medium' | 'low';
  tags: string[];
  dueDate?: string; // ISO string
  isRecurring: boolean;
  createdAt: string; // ISO string
  completedAt?: string; // ISO string
}

const TaskDisplay: React.FC<TaskProps> = ({
  id,
  title,
  description,
  status,
  priority,
  tags,
  dueDate,
  isRecurring,
  createdAt,
  completedAt
}) => {
  // Helper function to format dates
  const formatDate = (dateString?: string): string => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Helper function to get priority color
  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'high':
        return 'red';
      case 'medium':
        return 'orange';
      case 'low':
        return 'green';
      default:
        return 'gray';
    }
  };

  // Helper function to get priority text
  const getPriorityText = (priority: string): string => {
    switch (priority) {
      case 'high':
        return 'High';
      case 'medium':
        return 'Medium';
      case 'low':
        return 'Low';
      default:
        return 'Medium';
    }
  };

  // Check if task is overdue
  const isOverdue = (): boolean => {
    if (!dueDate || status === 'completed') return false;
    const due = new Date(dueDate);
    const now = new Date();
    return due < now && status !== 'completed';
  };

  // Check if due today
  const isDueToday = (): boolean => {
    if (!dueDate || status === 'completed') return false;
    const due = new Date(dueDate);
    const today = new Date();
    return (
      due.getDate() === today.getDate() &&
      due.getMonth() === today.getMonth() &&
      due.getFullYear() === today.getFullYear()
    );
  };

  return (
    <div className={`task-card ${status} ${isOverdue() ? 'overdue' : ''}`}>
      <div className="task-header">
        <h3 className="task-title">{title}</h3>
        <div className="task-meta">
          <span className={`priority-badge ${priority}`} style={{ backgroundColor: getPriorityColor(priority) }}>
            {getPriorityText(priority)}
          </span>
          {isRecurring && (
            <span className="recurring-badge">🔄 Recurring</span>
          )}
          {status === 'completed' && (
            <span className="status-badge completed">✓ Completed</span>
          )}
          {status === 'pending' && (
            <span className="status-badge pending">○ Pending</span>
          )}
        </div>
      </div>

      {description && (
        <div className="task-description">
          <p>{description}</p>
        </div>
      )}

      <div className="task-details">
        {dueDate && (
          <div className={`due-date ${isOverdue() ? 'overdue' : ''} ${isDueToday() ? 'due-today' : ''}`}>
            📅 Due: {formatDate(dueDate)}
            {isOverdue() && <span className="overdue-label">OVERDUE</span>}
            {isDueToday() && !isOverdue() && <span className="due-today-label">DUE TODAY</span>}
          </div>
        )}

        {tags.length > 0 && (
          <div className="task-tags">
            {tags.map((tag, index) => (
              <span key={index} className="tag-badge">
                #{tag}
              </span>
            ))}
          </div>
        )}

        <div className="task-timestamps">
          <small>Created: {formatDate(createdAt)}</small>
          {completedAt && <small>Completed: {formatDate(completedAt)}</small>}
        </div>
      </div>
    </div>
  );
};

export default TaskDisplay;