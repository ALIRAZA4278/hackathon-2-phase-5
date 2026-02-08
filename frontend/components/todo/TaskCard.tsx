"use client";

/**
 * TaskCard component for displaying a single task.
 * Per specs/ui/components.md - Phase V extended with priority, tags, due date, reminder.
 */
import { useState, useRef, useEffect } from "react";
import { Task } from "@/lib/api";
import { Checkbox } from "@/components/ui";

interface TaskCardProps {
  task: Task;
  onToggleComplete: (taskId: number) => void;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
  onClick?: (task: Task) => void;
}

// Get priority styling based on actual task.priority field
function getPriorityConfig(priority: "low" | "medium" | "high" | "urgent") {
  switch (priority) {
    case "urgent":
      return {
        label: "Urgent",
        bgColor: "bg-red-50",
        textColor: "text-red-700",
        borderColor: "border-red-200",
        dotColor: "bg-red-500",
      };
    case "high":
      return {
        label: "High",
        bgColor: "bg-orange-50",
        textColor: "text-orange-700",
        borderColor: "border-orange-200",
        dotColor: "bg-orange-500",
      };
    case "medium":
      return {
        label: "Medium",
        bgColor: "bg-blue-50",
        textColor: "text-blue-700",
        borderColor: "border-blue-200",
        dotColor: "bg-blue-500",
      };
    case "low":
    default:
      return {
        label: "Low",
        bgColor: "bg-gray-50",
        textColor: "text-gray-600",
        borderColor: "border-gray-200",
        dotColor: "bg-gray-400",
      };
  }
}

export function TaskCard({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
  onClick,
}: TaskCardProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const priority = task.priority || "medium";
  const priorityConfig = getPriorityConfig(priority);

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;

    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
    });
  };

  // Get relative time for display
  const getRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return formatDate(dateString);
  };

  // Format due date with overdue detection
  const formatDueDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
      hour: "numeric",
      minute: "2-digit",
    });
  };

  const isDueDateOverdue = (dateString: string) => {
    return new Date(dateString) < new Date();
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node)
      ) {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div
      className={`
        group relative bg-white border rounded-xl p-4 overflow-visible
        transition-all duration-200 ease-out
        ${
          task.completed
            ? "border-gray-100 bg-gray-50/50"
            : "border-gray-200 hover:border-blue-200 hover:shadow-lg hover:shadow-blue-500/5"
        }
        ${isHovered && !task.completed ? "scale-[1.01]" : "scale-100"}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Priority indicator bar */}
      <div
        className={`absolute left-0 top-4 bottom-4 w-1 rounded-full transition-opacity duration-200 ${
          task.completed ? "opacity-30" : "opacity-100"
        } ${priorityConfig.dotColor}`}
      />

      <div className="flex items-start gap-4 pl-3">
        {/* Drag Handle (visual placeholder) */}
        <div
          className={`
          flex-shrink-0 pt-1.5 cursor-grab active:cursor-grabbing
          transition-opacity duration-200
          ${isHovered ? "opacity-100" : "opacity-0"}
        `}
        >
          <svg
            className="w-4 h-4 text-gray-400"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M8 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm0 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm0 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm8-12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm0 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm0 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0z" />
          </svg>
        </div>

        {/* Checkbox */}
        <div className="pt-0.5">
          <Checkbox
            checked={task.completed}
            onChange={() => onToggleComplete(task.id)}
            aria-label={`Mark "${task.title}" as ${
              task.completed ? "incomplete" : "complete"
            }`}
          />
        </div>

        {/* Content */}
        <div
          className="flex-1 min-w-0 cursor-pointer"
          onClick={() => onClick?.(task)}
        >
          {/* Title */}
          <h3
            className={`
              font-medium leading-snug transition-colors duration-200
              ${
                task.completed
                  ? "line-through text-gray-400"
                  : "text-gray-900 group-hover:text-blue-600"
              }
            `}
          >
            {task.title}
          </h3>

          {/* Description */}
          {task.description && (
            <p
              className={`
                mt-1.5 text-sm leading-relaxed line-clamp-2
                ${task.completed ? "text-gray-400" : "text-gray-600"}
              `}
            >
              {task.description}
            </p>
          )}

          {/* Meta info row */}
          <div className="mt-3 flex items-center gap-2 flex-wrap">
            {/* Priority Badge */}
            <span
              className={`
                inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium
                ${priorityConfig.bgColor} ${priorityConfig.textColor}
                ${task.completed ? "opacity-50" : ""}
              `}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${priorityConfig.dotColor}`}
              />
              {priorityConfig.label}
            </span>

            {/* Tags as chips/pills */}
            {task.tags &&
              task.tags.length > 0 &&
              task.tags.map((tag) => (
                <span
                  key={tag}
                  className={`
                    inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                    bg-blue-50 text-blue-700
                    ${task.completed ? "opacity-50" : ""}
                  `}
                >
                  {tag}
                </span>
              ))}

            {/* Due Date */}
            {task.due_date && (
              <span
                className={`
                  inline-flex items-center gap-1 text-xs
                  ${
                    task.completed
                      ? "text-gray-400"
                      : isDueDateOverdue(task.due_date)
                        ? "text-red-600 font-medium"
                        : "text-gray-500"
                  }
                `}
              >
                <svg
                  className="w-3.5 h-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                {!task.completed && isDueDateOverdue(task.due_date)
                  ? `Overdue: ${formatDueDate(task.due_date)}`
                  : formatDueDate(task.due_date)}
              </span>
            )}

            {/* Reminder Indicator */}
            {task.reminder_time && (
              <span
                className={`
                  inline-flex items-center gap-1 text-xs
                  ${task.completed ? "text-gray-400" : "text-amber-600"}
                `}
                title={`Reminder: ${formatDueDate(task.reminder_time)}`}
              >
                <svg
                  className="w-3.5 h-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
              </span>
            )}

            {/* Created date */}
            <span
              className={`text-xs ${
                task.completed ? "text-gray-400" : "text-gray-500"
              }`}
            >
              <svg
                className="inline-block w-3.5 h-3.5 mr-1 -mt-0.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {getRelativeTime(task.created_at)}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1">
          {/* Quick complete button (visible on hover) */}
          {!task.completed && (
            <button
              onClick={() => onToggleComplete(task.id)}
              className={`
                p-2 rounded-lg text-gray-400 hover:text-green-600 hover:bg-green-50
                transition-all duration-200
                ${isHovered ? "opacity-100" : "opacity-0"}
              `}
              aria-label="Mark as complete"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </button>
          )}

          {/* Menu */}
          <div className="relative z-40" ref={menuRef}>
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className={`
                p-2 rounded-lg transition-all duration-200
                ${
                  isMenuOpen
                    ? "text-gray-600 bg-gray-100"
                    : "text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                }
              `}
              aria-label="Task options"
              aria-expanded={isMenuOpen}
              aria-haspopup="menu"
            >
              <svg
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
                />
              </svg>
            </button>

            {/* Dropdown menu */}
            {isMenuOpen && (
              <div
                className="absolute right-0 mt-2 w-44 bg-white rounded-xl shadow-xl border border-gray-100 py-1.5 z-50 animate-in fade-in slide-in-from-top-2 duration-200"
                role="menu"
              >
                <button
                  onClick={() => {
                    setIsMenuOpen(false);
                    onEdit(task);
                  }}
                  className="w-full px-3 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3 transition-colors"
                  role="menuitem"
                >
                  <svg
                    className="h-4 w-4 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                  Edit task
                </button>

                <button
                  onClick={() => {
                    setIsMenuOpen(false);
                    onToggleComplete(task.id);
                  }}
                  className="w-full px-3 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3 transition-colors"
                  role="menuitem"
                >
                  {task.completed ? (
                    <>
                      <svg
                        className="h-4 w-4 text-gray-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                        />
                      </svg>
                      Mark incomplete
                    </>
                  ) : (
                    <>
                      <svg
                        className="h-4 w-4 text-gray-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                      Mark complete
                    </>
                  )}
                </button>

                <div className="my-1.5 border-t border-gray-100" />

                <button
                  onClick={() => {
                    setIsMenuOpen(false);
                    onDelete(task);
                  }}
                  className="w-full px-3 py-2.5 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-3 transition-colors"
                  role="menuitem"
                >
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                  Delete task
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Completion overlay animation */}
      {task.completed && (
        <div className="absolute inset-0 bg-gradient-to-r from-green-50/50 to-transparent rounded-xl pointer-events-none" />
      )}
    </div>
  );
}
