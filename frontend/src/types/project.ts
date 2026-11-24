export interface Project {
  id: number
  name: string
  description: string | null
  owner_id: number
  created_at: string
  updated_at: string
}

export interface ProjectCreateInput {
  name: string
  description?: string
}

export interface ProjectUpdateInput {
  name?: string
  description?: string
}
