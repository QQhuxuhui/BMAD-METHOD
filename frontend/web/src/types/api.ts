// API响应通用格式
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

// 工作流状态
export type WorkflowStatus = 'running' | 'completed' | 'failed' | 'pending'

// 工作流类型
export interface Workflow {
  id: string
  name: string
  description?: string
  status: WorkflowStatus
  createdAt: string
  updatedAt: string
  startTime?: string
  endTime?: string
  duration?: number
  steps?: WorkflowStep[]
}

// 工作流步骤
export interface WorkflowStep {
  id: string
  name: string
  status: WorkflowStatus
  startTime?: string
  endTime?: string
  error?: string
}

// 分页请求参数
export interface PaginationParams {
  page: number
  pageSize: number
  total?: number
}

// 分页响应
export interface PaginationResponse<T> {
  list: T[]
  pagination: {
    page: number
    pageSize: number
    total: number
  }
}
