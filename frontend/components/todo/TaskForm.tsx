"use client";

/**
 * TaskForm component for creating and editing tasks.
 * Per specs/ui/components.md
 */
import { useState, useEffect } from "react";
import { Task, TaskCreate, TaskUpdate } from "@/lib/api";
import { Button, Input, Textarea, Modal } from "@/components/ui";

interface TaskFormProps {
  isOpen: boolean;
  onClose: () => void;
  mode: "create" | "edit";
  task?: Task | null;
  onSubmit: (data: TaskCreate | TaskUpdate) => Promise<void>;
  isSubmitting: boolean;
}

export function TaskForm({
  isOpen,
  onClose,
  mode,
  task,
  onSubmit,
  isSubmitting,
}: TaskFormProps) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    priority: "medium" as "low" | "medium" | "high" | "urgent",
    tags: "",
    due_date: "",
    reminder_time: "",
  });
  const [errors, setErrors] = useState<{
    title?: string;
    description?: string;
    due_date?: string;
    reminder_time?: string;
  }>({});

  // Reset form when modal opens/closes or task changes
  useEffect(() => {
    if (isOpen && mode === "edit" && task) {
      setFormData({
        title: task.title,
        description: task.description || "",
        priority: task.priority || "medium",
        tags: task.tags ? task.tags.join(", ") : "",
        due_date: task.due_date
          ? new Date(task.due_date).toISOString().slice(0, 16)
          : "",
        reminder_time: task.reminder_time
          ? new Date(task.reminder_time).toISOString().slice(0, 16)
          : "",
      });
    } else if (isOpen && mode === "create") {
      setFormData({
        title: "",
        description: "",
        priority: "medium",
        tags: "",
        due_date: "",
        reminder_time: "",
      });
    }
    setErrors({});
  }, [isOpen, mode, task]);

  // Validate form
  const validateForm = () => {
    const newErrors: typeof errors = {};

    if (!formData.title.trim()) {
      newErrors.title = "Title is required";
    } else if (formData.title.length > 200) {
      newErrors.title = "Title must be 200 characters or less";
    }

    if (formData.description.length > 1000) {
      newErrors.description = "Description must be 1000 characters or less";
    }

    if (formData.reminder_time && formData.due_date) {
      const reminder = new Date(formData.reminder_time);
      const due = new Date(formData.due_date);
      if (reminder > due) {
        newErrors.reminder_time = "Reminder must be before the due date";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    // Parse tags from comma-separated string
    const tagsArray = formData.tags
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);

    await onSubmit({
      title: formData.title.trim(),
      description: formData.description.trim() || null,
      priority: formData.priority,
      tags: tagsArray.length > 0 ? tagsArray : [],
      due_date: formData.due_date
        ? new Date(formData.due_date).toISOString()
        : null,
      reminder_time: formData.reminder_time
        ? new Date(formData.reminder_time).toISOString()
        : null,
    });
  };

  const title = mode === "create" ? "Create Task" : "Edit Task";
  const submitText = mode === "create" ? "Create" : "Save";

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Title"
          placeholder="Enter task title"
          value={formData.title}
          onChange={(e) =>
            setFormData((prev) => ({ ...prev, title: e.target.value }))
          }
          error={errors.title}
          required
          disabled={isSubmitting}
          maxLength={200}
        />

        <Textarea
          label="Description"
          placeholder="Enter task description (optional)"
          value={formData.description}
          onChange={(e) =>
            setFormData((prev) => ({ ...prev, description: e.target.value }))
          }
          error={errors.description}
          disabled={isSubmitting}
          maxLength={1000}
          showCount
          rows={4}
        />

        {/* Priority Selector */}
        <div className="w-full">
          <label
            htmlFor="task-priority"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Priority
          </label>
          <select
            id="task-priority"
            value={formData.priority}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                priority: e.target.value as typeof formData.priority,
              }))
            }
            disabled={isSubmitting}
            className="w-full px-3 py-2 text-base text-gray-800 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors duration-150"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        {/* Tags Input */}
        <Input
          label="Tags"
          placeholder="e.g. work, personal, urgent (comma-separated)"
          value={formData.tags}
          onChange={(e) =>
            setFormData((prev) => ({ ...prev, tags: e.target.value }))
          }
          disabled={isSubmitting}
        />

        {/* Due Date and Reminder Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Due Date Picker */}
          <div className="w-full">
            <label
              htmlFor="task-due-date"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Due Date
            </label>
            <input
              id="task-due-date"
              type="datetime-local"
              value={formData.due_date}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, due_date: e.target.value }))
              }
              disabled={isSubmitting}
              className={`
                w-full px-3 py-2 text-base text-gray-800
                bg-white border rounded-md
                placeholder:text-gray-400
                focus:outline-none focus:ring-2 focus:border-transparent
                disabled:bg-gray-100 disabled:cursor-not-allowed
                transition-colors duration-150
                ${errors.due_date ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-blue-500"}
              `}
            />
            {errors.due_date && (
              <p className="mt-1 text-sm text-red-600" role="alert">
                {errors.due_date}
              </p>
            )}
          </div>

          {/* Reminder Time Picker */}
          <div className="w-full">
            <label
              htmlFor="task-reminder"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Reminder
            </label>
            <input
              id="task-reminder"
              type="datetime-local"
              value={formData.reminder_time}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  reminder_time: e.target.value,
                }))
              }
              disabled={isSubmitting}
              className={`
                w-full px-3 py-2 text-base text-gray-800
                bg-white border rounded-md
                placeholder:text-gray-400
                focus:outline-none focus:ring-2 focus:border-transparent
                disabled:bg-gray-100 disabled:cursor-not-allowed
                transition-colors duration-150
                ${errors.reminder_time ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-blue-500"}
              `}
            />
            {errors.reminder_time && (
              <p className="mt-1 text-sm text-red-600" role="alert">
                {errors.reminder_time}
              </p>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button type="submit" loading={isSubmitting} disabled={isSubmitting}>
            {submitText}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
