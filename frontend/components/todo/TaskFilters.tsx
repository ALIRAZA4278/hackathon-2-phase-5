"use client";

/**
 * TaskFilters component for filtering tasks by priority, status, tags, and date range.
 * Per specs/features/task-crud.md - Phase V advanced filtering.
 */
import { useState, useEffect } from "react";
import type { TaskQueryParams } from "@/types/task";

interface TaskFiltersProps {
  onFilterChange: (filters: Partial<TaskQueryParams>) => void;
  activeFilters: Partial<TaskQueryParams>;
}

const PRIORITY_OPTIONS = [
  { value: "", label: "All Priorities" },
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "urgent", label: "Urgent" },
] as const;

const STATUS_OPTIONS = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "completed", label: "Completed" },
] as const;

export function TaskFilters({ onFilterChange, activeFilters }: TaskFiltersProps) {
  const [tags, setTags] = useState(activeFilters.tags || "");

  // Sync local tags state with activeFilters prop
  useEffect(() => {
    setTags(activeFilters.tags || "");
  }, [activeFilters.tags]);

  const handlePriorityChange = (priority: string) => {
    onFilterChange({
      ...activeFilters,
      priority: priority
        ? (priority as TaskQueryParams["priority"])
        : undefined,
    });
  };

  const handleStatusChange = (status: string) => {
    onFilterChange({
      ...activeFilters,
      status: status as TaskQueryParams["status"],
    });
  };

  const handleTagsChange = (value: string) => {
    setTags(value);
    // Normalize: trim whitespace around commas
    const normalized = value
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean)
      .join(",");
    onFilterChange({
      ...activeFilters,
      tags: normalized || undefined,
    });
  };

  const handleDateFromChange = (value: string) => {
    onFilterChange({
      ...activeFilters,
      due_date_from: value || undefined,
    });
  };

  const handleDateToChange = (value: string) => {
    onFilterChange({
      ...activeFilters,
      due_date_to: value || undefined,
    });
  };

  const handleClearFilters = () => {
    setTags("");
    onFilterChange({});
  };

  const hasActiveFilters =
    activeFilters.priority ||
    (activeFilters.status && activeFilters.status !== "all") ||
    activeFilters.tags ||
    activeFilters.due_date_from ||
    activeFilters.due_date_to;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm space-y-4">
      {/* Status Tabs */}
      <div>
        <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
          Status
        </label>
        <div className="flex bg-gray-100 rounded-lg p-1">
          {STATUS_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleStatusChange(option.value)}
              className={`
                flex-1 px-3 py-1.5 text-sm font-medium rounded-md transition-all duration-200
                ${
                  (activeFilters.status || "all") === option.value
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }
              `}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Priority and Tags Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Priority Dropdown */}
        <div>
          <label
            htmlFor="filter-priority"
            className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-2"
          >
            Priority
          </label>
          <select
            id="filter-priority"
            value={activeFilters.priority || ""}
            onChange={(e) => handlePriorityChange(e.target.value)}
            className="w-full px-3 py-2 text-sm text-gray-800 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-150"
          >
            {PRIORITY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Tag Filter */}
        <div>
          <label
            htmlFor="filter-tags"
            className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-2"
          >
            Tags
          </label>
          <input
            id="filter-tags"
            type="text"
            placeholder="e.g. work, personal, urgent"
            value={tags}
            onChange={(e) => handleTagsChange(e.target.value)}
            className="w-full px-3 py-2 text-sm text-gray-800 bg-white border border-gray-300 rounded-md placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-150"
          />
        </div>
      </div>

      {/* Date Range Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="filter-date-from"
            className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-2"
          >
            Due Date From
          </label>
          <input
            id="filter-date-from"
            type="date"
            value={activeFilters.due_date_from || ""}
            onChange={(e) => handleDateFromChange(e.target.value)}
            className="w-full px-3 py-2 text-sm text-gray-800 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-150"
          />
        </div>
        <div>
          <label
            htmlFor="filter-date-to"
            className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-2"
          >
            Due Date To
          </label>
          <input
            id="filter-date-to"
            type="date"
            value={activeFilters.due_date_to || ""}
            onChange={(e) => handleDateToChange(e.target.value)}
            className="w-full px-3 py-2 text-sm text-gray-800 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-150"
          />
        </div>
      </div>

      {/* Clear Filters */}
      {hasActiveFilters && (
        <div className="flex justify-end pt-1">
          <button
            type="button"
            onClick={handleClearFilters}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors duration-150"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
}
