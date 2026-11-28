export interface SubtaskItem {
  title: string
  description?: string | null
}

export interface SubtaskSuggestionResponse {
  task_id: number
  task_title: string
  subtasks: SubtaskItem[]
}

export interface BatchTaskCreate {
  project_id: number
  tasks: SubtaskItem[]
}
