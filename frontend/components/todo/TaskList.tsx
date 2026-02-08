"use client";

/**
 * TaskList component for displaying a list of tasks with search, filters, and sort.
 * Per specs/ui/components.md - Phase V extended with advanced query controls.
 */
import { useState, useCallback } from "react";
import { Task } from "@/lib/api";
import type { TaskQueryParams } from "@/types/task";
import { TaskCard } from "./TaskCard";
import { TaskSearch } from "./TaskSearch";
import { TaskFilters } from "./TaskFilters";
import { TaskSort } from "./TaskSort";
import { EmptyState } from "./EmptyState";
import { TaskCardSkeleton } from "@/components/ui";
import { Button } from "@/components/ui";

interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  onToggleComplete: (taskId: number) => void;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
  onClick?: (task: Task) => void;
  onCreateClick: () => void;
  onQueryParamsChange?: (params: Partial<TaskQueryParams>) => void;
}

export function TaskList({
  tasks,
  isLoading,
  onToggleComplete,
  onEdit,
  onDelete,
  onClick,
  onCreateClick,
  onQueryParamsChange,
}: TaskListProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState<Partial<TaskQueryParams>>({});
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const [showFilters, setShowFilters] = useState(false);

  // Build and emit combined query params
  const emitQueryParams = useCallback(
    (
      newSearch?: string,
      newFilters?: Partial<TaskQueryParams>,
      newSortBy?: string,
      newSortOrder?: string
    ) => {
      const search = newSearch !== undefined ? newSearch : searchQuery;
      const activeFilters = newFilters !== undefined ? newFilters : filters;
      const activeSortBy = newSortBy !== undefined ? newSortBy : sortBy;
      const activeSortOrder = newSortOrder !== undefined ? newSortOrder : sortOrder;

      const params: Partial<TaskQueryParams> = {
        ...activeFilters,
        search: search || undefined,
        sort_by: activeSortBy as TaskQueryParams["sort_by"],
        sort_order: activeSortOrder as TaskQueryParams["sort_order"],
      };

      onQueryParamsChange?.(params);
    },
    [searchQuery, filters, sortBy, sortOrder, onQueryParamsChange]
  );

  const handleSearch = useCallback(
    (query: string) => {
      setSearchQuery(query);
      emitQueryParams(query, undefined, undefined, undefined);
    },
    [emitQueryParams]
  );

  const handleFilterChange = useCallback(
    (newFilters: Partial<TaskQueryParams>) => {
      setFilters(newFilters);
      emitQueryParams(undefined, newFilters, undefined, undefined);
    },
    [emitQueryParams]
  );

  const handleSortChange = useCallback(
    (newSortBy: string, newSortOrder: string) => {
      setSortBy(newSortBy);
      setSortOrder(newSortOrder);
      emitQueryParams(undefined, undefined, newSortBy, newSortOrder);
    },
    [emitQueryParams]
  );

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <TaskCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  // Empty state (no tasks at all)
  if (tasks.length === 0 && !searchQuery && Object.keys(filters).length === 0) {
    return (
      <EmptyState
        action={
          <Button onClick={onCreateClick}>
            <svg
              className="h-5 w-5 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Create Task
          </Button>
        }
      />
    );
  }

  return (
    <div className="space-y-4">
      {/* Search, Sort, and Filter Controls */}
      <div className="space-y-3">
        {/* Search and Sort Row */}
        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
          <div className="flex-1 w-full">
            <TaskSearch onSearch={handleSearch} initialValue={searchQuery} />
          </div>
          <div className="flex items-center gap-2">
            <TaskSort
              onSortChange={handleSortChange}
              currentSortBy={sortBy}
              currentSortOrder={sortOrder}
            />
            {/* Toggle Filters Button */}
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`
                inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-md border transition-all duration-150
                ${
                  showFilters
                    ? "bg-blue-50 text-blue-700 border-blue-200"
                    : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
                }
              `}
              aria-label="Toggle filters"
              aria-expanded={showFilters}
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
                  d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
                />
              </svg>
              Filters
            </button>
          </div>
        </div>

        {/* Filters Panel (collapsible) */}
        {showFilters && (
          <TaskFilters
            onFilterChange={handleFilterChange}
            activeFilters={filters}
          />
        )}
      </div>

      {/* Task Cards */}
      {tasks.length > 0 ? (
        <div className="space-y-3 overflow-visible">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onToggleComplete={onToggleComplete}
              onEdit={onEdit}
              onDelete={onDelete}
              onClick={onClick}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-1">
            No tasks found
          </h3>
          <p className="text-gray-500">
            Try adjusting your search or filters.
          </p>
        </div>
      )}
    </div>
  );
}
