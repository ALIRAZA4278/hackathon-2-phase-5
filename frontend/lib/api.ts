/**
 * API client with JWT token attachment.
 * Per specs/api/rest-endpoints.md and specs/002-cloud-native-platform/contracts/tasks-api.md
 */
import type {
  Task,
  TaskListResponse,
  TaskCreate,
  TaskUpdate,
  TaskQueryParams,
  Reminder,
  ReminderCreate,
  ApiError,
} from "@/types/task";

// Re-export types for backward compatibility
export type {
  Task,
  TaskListResponse,
  TaskCreate,
  TaskUpdate,
  TaskQueryParams,
  Reminder,
  ReminderCreate,
  ApiError,
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Custom error class for API errors.
 */
export class ApiException extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
    this.name = "ApiException";
  }
}

/**
 * Make an authenticated API request.
 * Automatically attaches JWT token from Better Auth session.
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Get token from Better Auth session cookie
  // The token is automatically included via credentials: 'include'
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: "include", // Include cookies for authentication
  });

  // Handle no content response (DELETE)
  if (response.status === 204) {
    return undefined as T;
  }

  // Parse response
  const data = await response.json();

  // Handle errors
  if (!response.ok) {
    throw new ApiException(
      response.status,
      data.detail || "An unexpected error occurred"
    );
  }

  return data as T;
}

/**
 * Task API methods.
 */
export const tasksApi = {
  /**
   * List all tasks for the user with optional query parameters.
   * GET /api/{userId}/tasks
   * Backward compatible: params argument is optional.
   */
  list: async (
    userId: string,
    token: string,
    params?: Partial<TaskQueryParams>
  ): Promise<TaskListResponse> => {
    let queryString = "";
    if (params) {
      const searchParams = new URLSearchParams();
      if (params.search) searchParams.set("search", params.search);
      if (params.status && params.status !== "all")
        searchParams.set("status", params.status);
      if (params.priority) searchParams.set("priority", params.priority);
      if (params.tags) searchParams.set("tags", params.tags);
      if (params.due_date_from)
        searchParams.set("due_date_from", params.due_date_from);
      if (params.due_date_to)
        searchParams.set("due_date_to", params.due_date_to);
      if (params.sort_by) searchParams.set("sort_by", params.sort_by);
      if (params.sort_order) searchParams.set("sort_order", params.sort_order);
      const qs = searchParams.toString();
      if (qs) queryString = `?${qs}`;
    }
    return apiRequest<TaskListResponse>(
      `/api/${userId}/tasks${queryString}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
  },

  /**
   * Create a new task.
   * POST /api/{userId}/tasks
   */
  create: async (
    userId: string,
    data: TaskCreate,
    token: string
  ): Promise<Task> => {
    return apiRequest<Task>(`/api/${userId}/tasks`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    });
  },

  /**
   * Get a single task by ID.
   * GET /api/{userId}/tasks/{taskId}
   */
  get: async (userId: string, taskId: number, token: string): Promise<Task> => {
    return apiRequest<Task>(`/api/${userId}/tasks/${taskId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  /**
   * Update a task.
   * PUT /api/{userId}/tasks/{taskId}
   */
  update: async (
    userId: string,
    taskId: number,
    data: TaskUpdate,
    token: string
  ): Promise<Task> => {
    return apiRequest<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a task.
   * DELETE /api/{userId}/tasks/{taskId}
   */
  delete: async (
    userId: string,
    taskId: number,
    token: string
  ): Promise<void> => {
    await apiRequest<void>(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  /**
   * Toggle task completion status.
   * PATCH /api/{userId}/tasks/{taskId}/complete
   */
  toggleComplete: async (
    userId: string,
    taskId: number,
    token: string
  ): Promise<Task> => {
    return apiRequest<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  /**
   * Set a reminder for a task.
   * POST /api/{userId}/tasks/{taskId}/reminder
   */
  setReminder: async (
    userId: string,
    taskId: number,
    data: ReminderCreate,
    token: string
  ): Promise<Reminder> => {
    return apiRequest<Reminder>(
      `/api/${userId}/tasks/${taskId}/reminder`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Cancel a reminder for a task.
   * DELETE /api/{userId}/tasks/{taskId}/reminder
   */
  cancelReminder: async (
    userId: string,
    taskId: number,
    token: string
  ): Promise<void> => {
    await apiRequest<void>(
      `/api/${userId}/tasks/${taskId}/reminder`,
      {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      }
    );
  },
};
