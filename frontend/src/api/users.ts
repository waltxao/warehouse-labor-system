import client from './client'

/** 用户列表 */
export function getUsers() {
  return client.get('/users')
}

/** 创建用户 */
export function createUser(data: any) {
  return client.post('/users', data)
}
