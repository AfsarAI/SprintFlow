import React, { useEffect, useState } from 'react'
import {
  batchCreateTasks,
  createProject,
  createTask,
  deleteProject,
  deleteTask,
  getProjects,
  getTasks,
  suggestSubtasks,
  updateProject,
  updateTask,
} from '../services/api'
import type {
  Project,
  ProjectCreateInput,
  SubtaskItem,
  Task,
  TaskCreateInput,
  TaskPriority,
  TaskStatus,
  User,
} from '../types'

interface WorkspaceProps {
  user: User
  onLogout: () => void
}

interface EditableSubtask extends SubtaskItem {
  id: string
  selected: boolean
}

export const Workspace: React.FC<WorkspaceProps> = ({ user, onLogout }) => {
  const [projects, setProjects] = useState<Project[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [actionError, setActionError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Filtering states
  const [selectedProjectId, setSelectedProjectId] = useState<number | 'all'>('all')
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'all'>('all')
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | 'all'>('all')

  // Project Modal/Form states
  const [showProjectModal, setShowProjectModal] = useState(false)
  const [editingProject, setEditingProject] = useState<Project | null>(null)
  const [projectName, setProjectName] = useState('')
  const [projectDescription, setProjectDescription] = useState('')

  // Task Modal/Form states
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [taskTitle, setTaskTitle] = useState('')
  const [taskDescription, setTaskDescription] = useState('')
  const [taskProjectId, setTaskProjectId] = useState<number>(0)
  const [taskStatus, setTaskStatus] = useState<TaskStatus>('todo')
  const [taskPriority, setTaskPriority] = useState<TaskPriority>('medium')
  const [taskDueDate, setTaskDueDate] = useState('')

  // AI Subtasks Modal states
  const [showAiModal, setShowAiModal] = useState(false)
  const [aiTargetTask, setAiTargetTask] = useState<Task | null>(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiError, setAiError] = useState<string | null>(null)
  const [aiSubtasks, setAiSubtasks] = useState<EditableSubtask[]>([])
  const [aiSaving, setAiSaving] = useState(false)

  // Fetch initial data
  const fetchData = async () => {
    setLoading(true)
    setActionError(null)
    try {
      const [projs, tsks] = await Promise.all([getProjects(), getTasks()])
      setProjects(projs)
      setTasks(tsks)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setActionError(err.message)
      } else {
        setActionError('Failed to load workspace data.')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void fetchData()
  }, [])

  const showSuccess = (msg: string) => {
    setSuccessMessage(msg)
    setTimeout(() => setSuccessMessage(null), 4000)
  }

  // Project actions
  const handleOpenCreateProject = () => {
    setEditingProject(null)
    setProjectName('')
    setProjectDescription('')
    setShowProjectModal(true)
  }

  const handleOpenEditProject = (proj: Project) => {
    setEditingProject(proj)
    setProjectName(proj.name)
    setProjectDescription(proj.description || '')
    setShowProjectModal(true)
  }

  const handleSaveProject = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!projectName.trim()) return

    try {
      if (editingProject) {
        const updated = await updateProject(editingProject.id, {
          name: projectName.trim(),
          description: projectDescription.trim() || undefined,
        })
        setProjects(projects.map((p) => (p.id === updated.id ? updated : p)))
        showSuccess('Project updated successfully.')
      } else {
        const input: ProjectCreateInput = {
          name: projectName.trim(),
          description: projectDescription.trim() || undefined,
        }
        const created = await createProject(input)
        setProjects([...projects, created])
        showSuccess('Project created successfully.')
      }
      setShowProjectModal(false)
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to save project.')
    }
  }

  const handleDeleteProject = async (id: number) => {
    if (!window.confirm('Delete this project and all its associated tasks?')) return
    try {
      await deleteProject(id)
      setProjects(projects.filter((p) => p.id !== id))
      setTasks(tasks.filter((t) => t.project_id !== id))
      if (selectedProjectId === id) setSelectedProjectId('all')
      showSuccess('Project deleted.')
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to delete project.')
    }
  }

  // Task actions
  const handleOpenCreateTask = (projectId?: number) => {
    const defaultProjId =
      projectId || (selectedProjectId !== 'all' ? selectedProjectId : projects[0]?.id || 0)
    setEditingTask(null)
    setTaskTitle('')
    setTaskDescription('')
    setTaskProjectId(defaultProjId)
    setTaskStatus('todo')
    setTaskPriority('medium')
    setTaskDueDate('')
    setShowTaskModal(true)
  }

  const handleOpenEditTask = (task: Task) => {
    setEditingTask(task)
    setTaskTitle(task.title)
    setTaskDescription(task.description || '')
    setTaskProjectId(task.project_id)
    setTaskStatus(task.status)
    setTaskPriority(task.priority)
    setTaskDueDate(task.due_date ? task.due_date.substring(0, 10) : '')
    setShowTaskModal(true)
  }

  const handleSaveTask = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!taskTitle.trim() || !taskProjectId) return

    try {
      if (editingTask) {
        const updated = await updateTask(editingTask.id, {
          title: taskTitle.trim(),
          description: taskDescription.trim() || undefined,
          status: taskStatus,
          priority: taskPriority,
          due_date: taskDueDate ? new Date(taskDueDate).toISOString() : null,
        })
        setTasks(tasks.map((t) => (t.id === updated.id ? updated : t)))
        showSuccess('Task updated successfully.')
      } else {
        const input: TaskCreateInput = {
          title: taskTitle.trim(),
          description: taskDescription.trim() || undefined,
          status: taskStatus,
          priority: taskPriority,
          due_date: taskDueDate ? new Date(taskDueDate).toISOString() : null,
          project_id: taskProjectId,
        }
        const created = await createTask(input)
        setTasks([...tasks, created])
        showSuccess('Task created successfully.')
      }
      setShowTaskModal(false)
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to save task.')
    }
  }

  const handleStatusChange = async (task: Task, newStatus: TaskStatus) => {
    try {
      const updated = await updateTask(task.id, { status: newStatus })
      setTasks(tasks.map((t) => (t.id === updated.id ? updated : t)))
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to update task status.')
    }
  }

  const handleDeleteTask = async (id: number) => {
    if (!window.confirm('Delete this task?')) return
    try {
      await deleteTask(id)
      setTasks(tasks.filter((t) => t.id !== id))
      showSuccess('Task deleted.')
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to delete task.')
    }
  }

  // AI Subtask Suggestions actions
  const handleOpenAiSubtasks = async (task: Task) => {
    setAiTargetTask(task)
    setShowAiModal(true)
    setAiLoading(true)
    setAiError(null)
    setAiSubtasks([])

    try {
      const result = await suggestSubtasks(task.id)
      const mapped: EditableSubtask[] = result.subtasks.map((item, index) => ({
        ...item,
        id: `ai-sub-${index}-${Date.now()}`,
        selected: true,
      }))
      setAiSubtasks(mapped)
    } catch (err: unknown) {
      setAiError(err instanceof Error ? err.message : 'Failed to generate suggestions.')
    } finally {
      setAiLoading(false)
    }
  }

  const handleToggleSubtask = (id: string) => {
    setAiSubtasks((prev) =>
      prev.map((item) => (item.id === id ? { ...item, selected: !item.selected } : item))
    )
  }

  const handleUpdateSubtaskField = (id: string, field: 'title' | 'description', val: string) => {
    setAiSubtasks((prev) =>
      prev.map((item) => (item.id === id ? { ...item, [field]: val } : item))
    )
  }

  const handleApproveSubtasks = async () => {
    if (!aiTargetTask) return
    const approved = aiSubtasks.filter((item) => item.selected && item.title.trim() !== '')
    if (approved.length === 0) {
      setAiError('Please select at least one subtask with a non-empty title.')
      return
    }

    setAiSaving(true)
    setAiError(null)
    try {
      const payload: SubtaskItem[] = approved.map((item) => ({
        title: item.title.trim(),
        description: item.description?.trim() || null,
      }))
      const created = await batchCreateTasks({
        project_id: aiTargetTask.project_id,
        tasks: payload,
      })
      setTasks((prev) => [...prev, ...created])
      setShowAiModal(false)
      showSuccess(`Approved and saved ${created.length} subtask(s) into project!`)
    } catch (err: unknown) {
      setAiError(err instanceof Error ? err.message : 'Failed to save subtasks.')
    } finally {
      setAiSaving(false)
    }
  }

  // Summary Metrics
  const totalProjects = projects.length
  const totalTasks = tasks.length
  const completedTasks = tasks.filter((t) => t.status === 'done').length
  const inProgressTasks = tasks.filter((t) => t.status === 'in_progress').length
  const highPriorityTasks = tasks.filter((t) => t.priority === 'high' && t.status !== 'done').length

  // Filtered tasks
  const filteredTasks = tasks.filter((task) => {
    if (selectedProjectId !== 'all' && task.project_id !== selectedProjectId) return false
    if (statusFilter !== 'all' && task.status !== statusFilter) return false
    if (priorityFilter !== 'all' && task.priority !== priorityFilter) return false
    return true
  })

  return (
    <div className="workspace">
      {/* Header Bar */}
      <div className="workspace-header">
        <div className="user-info">
          <span className="user-avatar">{user.email.charAt(0).toUpperCase()}</span>
          <div>
            <span className="user-email">{user.email}</span>
            <span className="user-badge">Authenticated • Owner</span>
          </div>
        </div>
        <div className="workspace-actions">
          <button onClick={onLogout} className="btn btn-secondary btn-sm">
            Sign Out
          </button>
        </div>
      </div>

      {actionError && (
        <div className="alert-error" role="alert">
          {actionError}
          <button className="close-btn" onClick={() => setActionError(null)}>
            ×
          </button>
        </div>
      )}

      {successMessage && (
        <div className="alert-success" role="status">
          {successMessage}
          <button className="close-btn" onClick={() => setSuccessMessage(null)}>
            ×
          </button>
        </div>
      )}

      {/* Metrics Overview Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-label">Total Projects</span>
          <span className="stat-value purple-text">{totalProjects}</span>
          <span className="stat-sub">Active Workspaces</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Total Tasks</span>
          <span className="stat-value blue-text">{totalTasks}</span>
          <span className="stat-sub">{inProgressTasks} In Progress</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Completed</span>
          <span className="stat-value green-text">{completedTasks}</span>
          <span className="stat-sub">
            {totalTasks > 0 ? `${Math.round((completedTasks / totalTasks) * 100)}% done` : 'No tasks yet'}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-label">High Priority</span>
          <span className="stat-value red-text">{highPriorityTasks}</span>
          <span className="stat-sub">Needs Attention</span>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">Loading your workspace...</div>
      ) : (
        <>
          {/* Projects Section */}
          <section className="section-block">
            <div className="section-header">
              <div>
                <h2>Projects ({projects.length})</h2>
                <p>Organize workstreams, repositories, and product milestones.</p>
              </div>
              <button onClick={handleOpenCreateProject} className="btn btn-primary">
                + New Project
              </button>
            </div>

            {projects.length === 0 ? (
              <div className="empty-state">
                <p>No projects created yet. Start by creating your first project!</p>
                <button onClick={handleOpenCreateProject} className="btn btn-primary btn-sm">
                  Create Project
                </button>
              </div>
            ) : (
              <div className="project-grid">
                {projects.map((project) => {
                  const projectTaskCount = tasks.filter((t) => t.project_id === project.id).length
                  const isSelected = selectedProjectId === project.id

                  return (
                    <div
                      key={project.id}
                      className={`project-card ${isSelected ? 'selected' : ''}`}
                    >
                      <div className="project-card-header">
                        <span className="project-tag">ID: {project.id}</span>
                        <div className="card-actions">
                          <button
                            onClick={() => handleOpenEditProject(project)}
                            className="btn-icon"
                            title="Edit project"
                          >
                            ✎
                          </button>
                          <button
                            onClick={() => handleDeleteProject(project.id)}
                            className="btn-icon delete"
                            title="Delete project"
                          >
                            🗑
                          </button>
                        </div>
                      </div>
                      <h3>{project.name}</h3>
                      <p className="project-desc">
                        {project.description || 'No description provided.'}
                      </p>
                      <div className="project-card-footer">
                        <span className="task-count">{projectTaskCount} tasks</span>
                        <div className="card-footer-buttons">
                          <button
                            onClick={() => handleOpenCreateTask(project.id)}
                            className="btn btn-xs btn-outline"
                            title="Add task to this project"
                          >
                            + Task
                          </button>
                          <button
                            onClick={() =>
                              setSelectedProjectId(selectedProjectId === project.id ? 'all' : project.id)
                            }
                            className={`btn btn-xs ${isSelected ? 'btn-active' : 'btn-outline'}`}
                          >
                            {isSelected ? 'Viewing' : 'Filter'}
                          </button>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </section>

          {/* Tasks Section */}
          <section className="section-block">
            <div className="section-header">
              <div>
                <h2>Tasks ({filteredTasks.length})</h2>
                <p>Manage deliverables, assign priorities, and generate AI subtasks.</p>
              </div>
              {projects.length > 0 && (
                <button onClick={() => handleOpenCreateTask()} className="btn btn-primary">
                  + New Task
                </button>
              )}
            </div>

            {/* Filter Controls */}
            <div className="filter-bar">
              <div className="filter-group">
                <label>Project:</label>
                <select
                  value={selectedProjectId}
                  onChange={(e) =>
                    setSelectedProjectId(e.target.value === 'all' ? 'all' : Number(e.target.value))
                  }
                >
                  <option value="all">All Projects</option>
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label>Status:</label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as TaskStatus | 'all')}
                >
                  <option value="all">All Statuses</option>
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Progress</option>
                  <option value="done">Done</option>
                </select>
              </div>

              <div className="filter-group">
                <label>Priority:</label>
                <select
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value as TaskPriority | 'all')}
                >
                  <option value="all">All Priorities</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              {(selectedProjectId !== 'all' || statusFilter !== 'all' || priorityFilter !== 'all') && (
                <button
                  onClick={() => {
                    setSelectedProjectId('all')
                    setStatusFilter('all')
                    priorityFilter !== 'all' && setPriorityFilter('all')
                  }}
                  className="btn btn-xs btn-outline"
                >
                  Reset Filters
                </button>
              )}
            </div>

            {/* Task List */}
            {filteredTasks.length === 0 ? (
              <div className="empty-state">
                <p>No tasks match the active filters.</p>
                {projects.length > 0 && (
                  <button onClick={() => handleOpenCreateTask()} className="btn btn-primary btn-sm">
                    Create Task
                  </button>
                )}
              </div>
            ) : (
              <div className="task-list">
                {filteredTasks.map((task) => {
                  const parentProject = projects.find((p) => p.id === task.project_id)

                  return (
                    <div key={task.id} className="task-row">
                      <div className="task-info">
                        <div className="task-meta">
                          <span className="project-badge">
                            {parentProject ? parentProject.name : `Project #${task.project_id}`}
                          </span>
                          <span className={`priority-badge ${task.priority}`}>
                            {task.priority.toUpperCase()}
                          </span>
                          {task.due_date && (
                            <span className="due-date-badge">
                              📅 {new Date(task.due_date).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                        <h4 className={task.status === 'done' ? 'task-done' : ''}>{task.title}</h4>
                        {task.description && <p className="task-desc">{task.description}</p>}
                      </div>

                      <div className="task-controls">
                        {/* AI Subtask Button */}
                        <button
                          onClick={() => handleOpenAiSubtasks(task)}
                          className="btn btn-xs btn-ai"
                          title="Generate AI subtask suggestions for this task"
                        >
                          ✨ AI Subtasks
                        </button>

                        <select
                          className={`status-select status-${task.status}`}
                          value={task.status}
                          onChange={(e) => handleStatusChange(task, e.target.value as TaskStatus)}
                        >
                          <option value="todo">To Do</option>
                          <option value="in_progress">In Progress</option>
                          <option value="done">Done</option>
                        </select>

                        <button
                          onClick={() => handleOpenEditTask(task)}
                          className="btn-icon"
                          title="Edit Task"
                        >
                          ✎
                        </button>
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="btn-icon delete"
                          title="Delete Task"
                        >
                          🗑
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </section>
        </>
      )}

      {/* Project Modal */}
      {showProjectModal && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <h3>{editingProject ? 'Edit Project' : 'Create New Project'}</h3>
            <form onSubmit={handleSaveProject}>
              <div className="form-group">
                <label>Project Name *</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="e.g. Mobile App Redesign"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  placeholder="Scope, goals, or sprint notes..."
                  rows={3}
                />
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  onClick={() => setShowProjectModal(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingProject ? 'Save Changes' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Task Modal */}
      {showTaskModal && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <h3>{editingTask ? 'Edit Task' : 'Create New Task'}</h3>
            <form onSubmit={handleSaveTask}>
              <div className="form-group">
                <label>Parent Project *</label>
                <select
                  value={taskProjectId}
                  onChange={(e) => setTaskProjectId(Number(e.target.value))}
                  disabled={!!editingTask}
                  required
                >
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Task Title *</label>
                <input
                  type="text"
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                  placeholder="e.g. Implement user authentication"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={taskDescription}
                  onChange={(e) => setTaskDescription(e.target.value)}
                  placeholder="Acceptance criteria, notes, or dependencies..."
                  rows={3}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Status</label>
                  <select
                    value={taskStatus}
                    onChange={(e) => setTaskStatus(e.target.value as TaskStatus)}
                  >
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="done">Done</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Priority</label>
                  <select
                    value={taskPriority}
                    onChange={(e) => setTaskPriority(e.target.value as TaskPriority)}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Due Date</label>
                <input
                  type="date"
                  value={taskDueDate}
                  onChange={(e) => setTaskDueDate(e.target.value)}
                />
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  onClick={() => setShowTaskModal(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingTask ? 'Save Changes' : 'Create Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* AI Subtasks Modal */}
      {showAiModal && aiTargetTask && (
        <div className="modal-backdrop">
          <div className="modal-content modal-ai">
            <div className="ai-modal-header">
              <span className="badge-ai">🤖 Generative AI</span>
              <h3>Subtask Breakdown Suggestions</h3>
              <p className="ai-modal-subtitle">
                Target Task: <strong>{aiTargetTask.title}</strong>
              </p>
            </div>

            {aiLoading ? (
              <div className="ai-loading-box">
                <div className="spinner"></div>
                <p>Generating intelligent task breakdown with Gemini...</p>
              </div>
            ) : aiError ? (
              <div className="ai-error-box">
                <div className="alert-error">{aiError}</div>
                <p className="ai-error-hint">
                  Make sure <code>GEMINI_API_KEY</code> is configured in <code>backend/.env</code> and restart the backend.
                </p>
                <div className="modal-footer">
                  <button onClick={() => setShowAiModal(false)} className="btn btn-secondary">
                    Close
                  </button>
                </div>
              </div>
            ) : (
              <div className="ai-results-box">
                <p className="ai-instructions">
                  Review the suggested subtasks below. Select which subtasks you want to approve and save into your project:
                </p>

                <div className="subtask-list">
                  {aiSubtasks.map((subtask) => (
                    <div
                      key={subtask.id}
                      className={`subtask-item ${subtask.selected ? 'checked' : ''}`}
                    >
                      <input
                        type="checkbox"
                        checked={subtask.selected}
                        onChange={() => handleToggleSubtask(subtask.id)}
                        className="subtask-checkbox"
                      />
                      <div className="subtask-inputs">
                        <input
                          type="text"
                          value={subtask.title}
                          onChange={(e) =>
                            handleUpdateSubtaskField(subtask.id, 'title', e.target.value)
                          }
                          className="subtask-title-input"
                          placeholder="Subtask title"
                        />
                        <input
                          type="text"
                          value={subtask.description || ''}
                          onChange={(e) =>
                            handleUpdateSubtaskField(subtask.id, 'description', e.target.value)
                          }
                          className="subtask-desc-input"
                          placeholder="Brief description or criteria..."
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="modal-footer">
                  <button
                    type="button"
                    onClick={() => setShowAiModal(false)}
                    className="btn btn-secondary"
                    disabled={aiSaving}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleApproveSubtasks}
                    className="btn btn-primary"
                    disabled={aiSaving || aiSubtasks.filter((s) => s.selected).length === 0}
                  >
                    {aiSaving
                      ? 'Saving Tasks...'
                      : `Approve & Save (${aiSubtasks.filter((s) => s.selected).length})`}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
