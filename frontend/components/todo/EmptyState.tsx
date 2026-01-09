"use client";

/**
 * EmptyState component for when there are no tasks.
 * Per specs/ui/components.md
 */
import { ReactNode } from "react";

interface EmptyStateProps {
  title?: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({
  title = "No tasks yet",
  description = "Create your first task to get started on your productivity journey",
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      {/* Illustration */}
      <div className="relative mb-8">
        {/* Background glow */}
        <div className="absolute inset-0 bg-blue-100 rounded-full blur-2xl opacity-60 scale-150"></div>

        {/* Main illustration container */}
        <div className="relative w-48 h-48">
          {/* Clipboard background */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-40 bg-gradient-to-b from-white to-gray-50 rounded-xl shadow-xl border border-gray-100 transform -rotate-6">
              {/* Clipboard clip */}
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-12 h-6 bg-gray-300 rounded-t-lg"></div>
              <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-8 h-3 bg-gray-400 rounded-full"></div>

              {/* Lines on clipboard */}
              <div className="absolute top-8 left-4 right-4 space-y-2">
                <div className="h-2 bg-gray-100 rounded-full w-3/4"></div>
                <div className="h-2 bg-gray-100 rounded-full w-full"></div>
                <div className="h-2 bg-gray-100 rounded-full w-2/3"></div>
              </div>
            </div>
          </div>

          {/* Floating checkmark */}
          <div className="absolute top-4 right-4 w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full shadow-lg shadow-green-500/30 flex items-center justify-center animate-bounce" style={{ animationDuration: '3s' }}>
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>

          {/* Floating plus */}
          <div className="absolute bottom-8 left-2 w-10 h-10 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full shadow-lg shadow-blue-500/30 flex items-center justify-center animate-pulse">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 6v12m6-6H6" />
            </svg>
          </div>

          {/* Floating star */}
          <div className="absolute top-12 left-6 w-8 h-8 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full shadow-lg shadow-amber-500/30 flex items-center justify-center" style={{ animation: 'pulse 4s ease-in-out infinite' }}>
            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>

          {/* Decorative dots */}
          <div className="absolute top-0 right-12 w-2 h-2 bg-purple-400 rounded-full animate-ping" style={{ animationDuration: '2s' }}></div>
          <div className="absolute bottom-4 right-8 w-3 h-3 bg-blue-300 rounded-full animate-ping" style={{ animationDuration: '3s' }}></div>
          <div className="absolute bottom-16 left-0 w-2 h-2 bg-green-400 rounded-full animate-ping" style={{ animationDuration: '2.5s' }}></div>
        </div>
      </div>

      {/* Title */}
      <h3 className="text-2xl font-bold text-gray-900 mb-2">{title}</h3>

      {/* Description */}
      <p className="text-gray-500 max-w-sm leading-relaxed mb-8">{description}</p>

      {/* Features hint */}
      <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
            <svg className="w-3.5 h-3.5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span>Quick to add</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-3.5 h-3.5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <span>Easy to track</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center">
            <svg className="w-3.5 h-3.5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <span>Always secure</span>
        </div>
      </div>

      {/* Action */}
      {action && (
        <div className="transform hover:scale-105 transition-transform duration-200">
          {action}
        </div>
      )}
    </div>
  );
}
