/**
 * TypeScript interfaces for Phase V advanced task attributes.
 * Synced with backend TaskResponse schema.
 * Per specs/002-cloud-native-platform/contracts/tasks-api.md
 */

/**
 * Recurring rule configuration.
 */
export interface RecurringRule {
  frequency: "daily" | "weekly" | "monthly" | "custom";
  interval?: number;
  day_of_week?: number;
  day_of_month?: number;
  cron_expression?: string;
  next_trigger_at?: string;
  is_active?: boolean;
}

/**
 * Task type matching backend TaskResponse schema (Phase V extended).
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: "low" | "medium" | "high" | "urgent";
  tags: string[];
  due_date: string | null;
  reminder_time: string | null;
  recurring_rule: RecurringRule | null;
  created_at: string;
  updated_at: string;
}

/**
 * Task list response type.
 */
export interface TaskListResponse {
  tasks: Task[];
  count: number;
}

/**
 * Task create request type (Phase V extended).
 */
export interface TaskCreate {
  title: string;
  description?: string | null;
  priority?: "low" | "medium" | "high" | "urgent";
  tags?: string[];
  due_date?: string | null;
  reminder_time?: string | null;
  recurring_rule?: RecurringRule | null;
}

/**
 * Task update request type (Phase V extended, all fields optional).
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
  priority?: "low" | "medium" | "high" | "urgent";
  tags?: string[];
  due_date?: string | null;
  reminder_time?: string | null;
  recurring_rule?: RecurringRule | null;
}

/**
 * Reminder response type.
 */
export interface Reminder {
  id: number;
  task_id: number;
  user_id: string;
  trigger_at: string;
  status: "pending" | "triggered" | "cancelled";
  created_at: string;
}

/**
 * Reminder create request type.
 */
export interface ReminderCreate {
  trigger_at: string;
}

/**
 * API error type.
 */
export interface ApiError {
  detail: string;
}

/**
 * Task query parameters for search, filter, sort.
 */
export interface TaskQueryParams {
  search?: string;
  status?: "all" | "pending" | "completed";
  priority?: "low" | "medium" | "high" | "urgent";
  tags?: string;
  due_date_from?: string;
  due_date_to?: string;
  sort_by?: "due_date" | "priority" | "created_at" | "updated_at";
  sort_order?: "asc" | "desc";
}
