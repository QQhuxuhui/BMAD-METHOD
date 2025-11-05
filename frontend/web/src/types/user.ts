// 用户信息
export interface User {
  id: string
  username: string
  email: string
  avatar?: string
  role: UserRole
  createdAt: string
}

// 用户角色
export type UserRole = 'admin' | 'user' | 'guest'

// 登录请求
export interface LoginRequest {
  username: string
  password: string
}

// 登录响应
export interface LoginResponse {
  token: string
  user: User
}
