"use client";

/**
 * TaskSort component for sorting tasks by various fields and order.
 * Per specs/features/task-crud.md - Phase V sort functionality.
 */

interface TaskSortProps {
  onSortChange: (sortBy: string, sortOrder: string) => void;
  currentSortBy?: string;
  currentSortOrder?: string;
}

const SORT_OPTIONS = [
  { value: "created_at", label: "Date Created" },
  { value: "updated_at", label: "Date Updated" },
  { value: "due_date", label: "Due Date" },
  { value: "priority", label: "Priority" },
] as const;

export function TaskSort({
  onSortChange,
  currentSortBy = "created_at",
  currentSortOrder = "desc",
}: TaskSortProps) {
  const handleSortByChange = (value: string) => {
    onSortChange(value, currentSortOrder);
  };

  const handleToggleOrder = () => {
    const newOrder = currentSortOrder === "asc" ? "desc" : "asc";
    onSortChange(currentSortBy, newOrder);
  };

  return (
    <div className="flex items-center gap-2">
      {/* Sort By Dropdown */}
      <div className="flex items-center gap-2">
        <label
          htmlFor="sort-by"
          className="text-sm font-medium text-gray-500 whitespace-nowrap"
        >
          Sort by
        </label>
        <select
          id="sort-by"
          value={currentSortBy}
          onChange={(e) => handleSortByChange(e.target.value)}
          className="px-3 py-2 text-sm text-gray-800 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-150"
        >
          {SORT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Sort Order Toggle */}
      <button
        type="button"
        onClick={handleToggleOrder}
        className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-150"
        aria-label={`Sort ${currentSortOrder === "asc" ? "descending" : "ascending"}`}
        title={currentSortOrder === "asc" ? "Ascending" : "Descending"}
      >
        {currentSortOrder === "asc" ? (
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
              d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
            />
          </svg>
        ) : (
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
              d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"
            />
          </svg>
        )}
        {currentSortOrder === "asc" ? "Asc" : "Desc"}
      </button>
    </div>
  );
}
