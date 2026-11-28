import type {
  BatchTaskCreate,
  HealthResponse,
  LoginInput,
  Project,
  ProjectCreateInput,
  ProjectUpdateInput,
  RegisterInput,
  SubtaskSuggestionResponse,
  Task,
  TaskCreateInput,
  TaskPriority,
  TaskStatus,
  TaskUpdateInput,
  TokenResponse,
  User,
} from '../types'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const TOKEN_KEY = 'sprintflow_access_token'

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeStoredToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  requireAuth = true
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const headers = new Headers(options.headers || {})

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  if (requireAuth) {
    const token = getStoredToken()
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (response.status === 401 && requireAuth) {
    removeStoredToken()
  }

  if (!response.ok) {
    let errorMessage = `Request failed (${response.status})`
    try {
      const errorData = await response.json()
      if (typeof errorData?.detail === 'string') {
        errorMessage = errorData.detail
      } else if (Array.isArray(errorData?.detail)) {
        errorMessage = errorData.detail.map((e: { msg?: string }) => e.msg || 'Validation error').join(', ')
      }
    } catch {
      // Body not JSON, keep default message
    }
    throw new Error(errorMessage)
  }

  if (response.status === 204) {
    return undefined as unknown as T
  }

  return response.json() as Promise<T>
}

// Health API
export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health', { method: 'GET' }, false)
}

// Auth API
export async function register(input: RegisterInput): Promise<User> {
  return request<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(input),
  }, false)
}

export async function login(input: LoginInput): Promise<TokenResponse> {
  const res = await request<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(input),
  }, false)
  if (res.access_token) {
    setStoredToken(res.access_token)
  }
  return res
}

export async function getMe(): Promise<User> {
  return request<User>('/auth/me', { method: 'GET' }, true)
}

// Project API
export async function getProjects(): Promise<Project[]> {
  return request<Project[]>('/projects', { method: 'GET' }, true)
}

export async function createProject(input: ProjectCreateInput): Promise<Project> {
  return request<Project>('/projects', {
    method: 'POST',
    body: JSON.stringify(input),
  }, true)
}

export async function getProject(id: number): Promise<Project> {
  return request<Project>(`/projects/${id}`, { method: 'GET' }, true)
}

export async function updateProject(id: number, input: ProjectUpdateInput): Promise<Project> {
  return request<Project>(`/projects/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  }, true)
}

export async function deleteProject(id: number): Promise<void> {
  return request<void>(`/projects/${id}`, { method: 'DELETE' }, true)
}

// Task API
export async function getTasks(params?: {
  project_id?: number
  status?: TaskStatus
  priority?: TaskPriority
}): Promise<Task[]> {
  const searchParams = new URLSearchParams()
  if (params?.project_id) searchParams.set('project_id', params.project_id.toString())
  if (params?.status) searchParams.set('status', params.status)
  if (params?.priority) searchParams.set('priority', params.priority)

  const query = searchParams.toString() ? `?${searchParams.toString()}` : ''
  return request<Task[]>(`/tasks${query}`, { method: 'GET' }, true)
}

export async function createTask(input: TaskCreateInput): Promise<Task> {
  return request<Task>('/tasks', {
    method: 'POST',
    body: JSON.stringify(input),
  }, true)
}

export async function batchCreateTasks(input: BatchTaskCreate): Promise<Task[]> {
  return request<Task[]>('/tasks/batch', {
    method: 'POST',
    body: JSON.stringify(input),
  }, true)
}

export async function getTask(id: number): Promise<Task> {
  return request<Task>(`/tasks/${id}`, { method: 'GET' }, true)
}

export async function updateTask(id: number, input: TaskUpdateInput): Promise<Task> {
  return request<Task>(`/tasks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  }, true)
}

export async function deleteTask(id: number): Promise<void> {
  return request<void>(`/tasks/${id}`, { method: 'DELETE' }, true)
}

// AI Subtask Suggestions API
export async function suggestSubtasks(taskId: number): Promise<SubtaskSuggestionResponse> {
  return request<SubtaskSuggestionResponse>(`/tasks/${taskId}/suggest-subtasks`, {
    method: 'POST',
  }, true)
}
