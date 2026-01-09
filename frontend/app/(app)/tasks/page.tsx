"use client";

/**
 * Tasks page - Main task management interface.
 * Per specs/ui/pages.md and specs/features/task-crud.md
 */
import { useState, useEffect, useCallback, useMemo } from "react";
import { useSession, getApiToken } from "@/lib/auth";
import { tasksApi, Task, TaskCreate, TaskUpdate, ApiException } from "@/lib/api";
import { Button, ToastProvider, useToast } from "@/components/ui";
import { TaskList, TaskForm, DeleteConfirmModal } from "@/components/todo";

type FilterType = "all" | "active" | "completed";

function TasksPageContent() {
  const { data: session } = useSession();
  const { showToast } = useToast();

  // State
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [formMode, setFormMode] = useState<"create" | "edit">("create");
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  // Filter and search state
  const [filter, setFilter] = useState<FilterType>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Get user ID and name from session
  const userId = session?.user?.id;
  const userName = session?.user?.name || session?.user?.email?.split("@")[0] || "there";

  // Fetch API token when session changes
  useEffect(() => {
    async function fetchToken() {
      if (session?.user) {
        const apiToken = await getApiToken();
        setToken(apiToken);
      }
    }
    fetchToken();
  }, [session]);

  // Fetch tasks
  const fetchTasks = useCallback(async () => {
    if (!userId || !token) return;

    try {
      setIsLoading(true);
      const response = await tasksApi.list(userId, token);
      setTasks(response.tasks);
    } catch (error) {
      if (error instanceof ApiException) {
        showToast(error.detail, "error");
      } else {
        showToast("Failed to load tasks", "error");
      }
    } finally {
      setIsLoading(false);
    }
  }, [userId, token, showToast]);

  // Load tasks on mount
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Filter and search tasks
  const filteredTasks = useMemo(() => {
    let result = tasks;

    // Apply filter
    if (filter === "active") {
      result = result.filter((t) => !t.completed);
    } else if (filter === "completed") {
      result = result.filter((t) => t.completed);
    }

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (t) =>
          t.title.toLowerCase().includes(query) ||
          t.description?.toLowerCase().includes(query)
      );
    }

    return result;
  }, [tasks, filter, searchQuery]);

  // Task statistics
  const stats = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter((t) => t.completed).length;
    const active = total - completed;
    const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;
    return { total, completed, active, completionRate };
  }, [tasks]);

  // Handle create task
  const handleCreate = async (data: TaskCreate | TaskUpdate) => {
    if (!userId || !token) return;

    setIsSubmitting(true);
    try {
      const newTask = await tasksApi.create(userId, data as TaskCreate, token);
      // Optimistic update - add to beginning of list
      setTasks((prev) => [newTask, ...prev]);
      setIsFormOpen(false);
      showToast("Task created successfully", "success");
    } catch (error) {
      if (error instanceof ApiException) {
        showToast(error.detail, "error");
      } else {
        showToast("Failed to create task", "error");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle update task
  const handleUpdate = async (data: TaskCreate | TaskUpdate) => {
    if (!userId || !token || !selectedTask) return;

    setIsSubmitting(true);
    try {
      const updatedTask = await tasksApi.update(
        userId,
        selectedTask.id,
        data as TaskUpdate,
        token
      );
      // Optimistic update
      setTasks((prev) =>
        prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
      );
      setIsFormOpen(false);
      setSelectedTask(null);
      showToast("Task updated successfully", "success");
    } catch (error) {
      if (error instanceof ApiException) {
        showToast(error.detail, "error");
      } else {
        showToast("Failed to update task", "error");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle toggle complete
  const handleToggleComplete = async (taskId: number) => {
    if (!userId || !token) return;

    // Find task for optimistic update
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    // Optimistic update
    setTasks((prev) =>
      prev.map((t) =>
        t.id === taskId ? { ...t, completed: !t.completed } : t
      )
    );

    try {
      await tasksApi.toggleComplete(userId, taskId, token);
    } catch (error) {
      // Revert on failure
      setTasks((prev) =>
        prev.map((t) =>
          t.id === taskId ? { ...t, completed: task.completed } : t
        )
      );
      if (error instanceof ApiException) {
        showToast(error.detail, "error");
      } else {
        showToast("Failed to update task", "error");
      }
    }
  };

  // Handle delete task
  const handleDelete = async () => {
    if (!userId || !token || !selectedTask) return;

    setIsDeleting(true);
    try {
      await tasksApi.delete(userId, selectedTask.id, token);
      // Remove from list
      setTasks((prev) => prev.filter((t) => t.id !== selectedTask.id));
      setIsDeleteModalOpen(false);
      setSelectedTask(null);
      showToast("Task deleted successfully", "success");
    } catch (error) {
      if (error instanceof ApiException) {
        showToast(error.detail, "error");
      } else {
        showToast("Failed to delete task", "error");
      }
    } finally {
      setIsDeleting(false);
    }
  };

  // Open create form
  const openCreateForm = () => {
    setFormMode("create");
    setSelectedTask(null);
    setIsFormOpen(true);
  };

  // Open edit form
  const openEditForm = (task: Task) => {
    setFormMode("edit");
    setSelectedTask(task);
    setIsFormOpen(true);
  };

  // Open delete confirmation
  const openDeleteModal = (task: Task) => {
    setSelectedTask(task);
    setIsDeleteModalOpen(true);
  };

  // Get greeting based on time of day
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Section */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
              {getGreeting()}, {userName.split(" ")[0]}!
            </h1>
            <p className="mt-1 text-gray-500">
              {stats.total === 0
                ? "Ready to be productive? Create your first task."
                : stats.active === 0
                ? "All caught up! Great job!"
                : `You have ${stats.active} task${stats.active !== 1 ? "s" : ""} to complete today.`}
            </p>
          </div>
          <Button
            onClick={openCreateForm}
            className="shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30 hover:-translate-y-0.5 transition-all duration-200"
          >
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
            Add Task
          </Button>
        </div>

        {/* Statistics Cards */}
        {stats.total > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
                  <div className="text-xs text-gray-500 font-medium">Total Tasks</div>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-amber-50 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{stats.active}</div>
                  <div className="text-xs text-gray-500 font-medium">In Progress</div>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{stats.completed}</div>
                  <div className="text-xs text-gray-500 font-medium">Completed</div>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{stats.completionRate}%</div>
                  <div className="text-xs text-gray-500 font-medium">Progress</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Progress Bar */}
        {stats.total > 0 && (
          <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Overall Progress</span>
              <span className="text-sm font-semibold text-blue-600">{stats.completionRate}%</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${stats.completionRate}%` }}
              />
            </div>
          </div>
        )}

        {/* Search and Filter */}
        {stats.total > 0 && (
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search Bar */}
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>

            {/* Filter Tabs */}
            <div className="flex bg-gray-100 rounded-xl p-1">
              {(["all", "active", "completed"] as FilterType[]).map((filterOption) => (
                <button
                  key={filterOption}
                  onClick={() => setFilter(filterOption)}
                  className={`
                    px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200
                    ${filter === filterOption
                      ? "bg-white text-gray-900 shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                    }
                  `}
                >
                  {filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
                  {filterOption !== "all" && (
                    <span className={`ml-1.5 text-xs ${filter === filterOption ? "text-blue-600" : "text-gray-400"}`}>
                      ({filterOption === "active" ? stats.active : stats.completed})
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Task list */}
      <TaskList
        tasks={filteredTasks}
        isLoading={isLoading}
        onToggleComplete={handleToggleComplete}
        onEdit={openEditForm}
        onDelete={openDeleteModal}
        onCreateClick={openCreateForm}
      />

      {/* No results message */}
      {!isLoading && filteredTasks.length === 0 && tasks.length > 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-1">No tasks found</h3>
          <p className="text-gray-500">
            {searchQuery
              ? `No tasks match "${searchQuery}"`
              : `No ${filter} tasks to display`}
          </p>
          {(searchQuery || filter !== "all") && (
            <button
              onClick={() => {
                setSearchQuery("");
                setFilter("all");
              }}
              className="mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Clear filters
            </button>
          )}
        </div>
      )}

      {/* Create/Edit form modal */}
      <TaskForm
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setSelectedTask(null);
        }}
        mode={formMode}
        task={selectedTask}
        onSubmit={formMode === "create" ? handleCreate : handleUpdate}
        isSubmitting={isSubmitting}
      />

      {/* Delete confirmation modal */}
      <DeleteConfirmModal
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setSelectedTask(null);
        }}
        task={selectedTask}
        onConfirm={handleDelete}
        isDeleting={isDeleting}
      />
    </div>
  );
}

export default function TasksPage() {
  return (
    <ToastProvider>
      <TasksPageContent />
    </ToastProvider>
  );
}
