import apiClient from './api'
import type { Workflow, ApiResponse } from '@/types/api'

export const workflowService = {
  // 获取工作流列表
  async getWorkflows(): Promise<ApiResponse<Workflow[]>> {
    return apiClient.get('/v1/workflows')
  },

  // 获取单个工作流详情
  async getWorkflowById(id: string): Promise<ApiResponse<Workflow>> {
    return apiClient.get(`/v1/workflows/${id}`)
  },

  // 创建工作流
  async createWorkflow(data: Partial<Workflow>): Promise<ApiResponse<Workflow>> {
    return apiClient.post('/v1/workflows', data)
  },

  // 更新工作流
  async updateWorkflow(id: string, data: Partial<Workflow>): Promise<ApiResponse<Workflow>> {
    return apiClient.put(`/v1/workflows/${id}`, data)
  },

  // 删除工作流
  async deleteWorkflow(id: string): Promise<ApiResponse<null>> {
    return apiClient.delete(`/v1/workflows/${id}`)
  },
}
