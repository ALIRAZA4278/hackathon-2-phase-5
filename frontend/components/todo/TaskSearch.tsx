"use client";

/**
 * TaskSearch component with debounced search input.
 * Per specs/features/task-crud.md - Phase V search functionality.
 */
import { useState, useEffect, useRef } from "react";

interface TaskSearchProps {
  onSearch: (query: string) => void;
  initialValue?: string;
}

export function TaskSearch({ onSearch, initialValue = "" }: TaskSearchProps) {
  const [query, setQuery] = useState(initialValue);
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isFirstRender = useRef(true);
  // Stable ref for onSearch to prevent effect re-triggers on callback identity change
  const onSearchRef = useRef(onSearch);
  onSearchRef.current = onSearch;

  // Sync with external initialValue changes
  useEffect(() => {
    setQuery(initialValue);
  }, [initialValue]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, []);

  // Trigger debounced search on query change only (skip first render)
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    debounceTimer.current = setTimeout(() => {
      onSearchRef.current(query);
    }, 300);
  }, [query]);

  const handleClear = () => {
    setQuery("");
    // Immediately fire onSearch when clearing
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    onSearch("");
  };

  return (
    <div className="relative">
      {/* Search Icon */}
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg
          className="h-5 w-5 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>

      {/* Search Input */}
      <input
        type="text"
        placeholder="Search tasks..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label="Search tasks"
        className="block w-full pl-10 pr-10 py-2.5 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
      />

      {/* Clear Button */}
      {query && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors duration-150"
          aria-label="Clear search"
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
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}
    </div>
  );
}
