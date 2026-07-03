import client from './client'

/** 告警规则列表 */
export function getRules() {
  return client.get('/alerts/rules')
}

/** 创建告警规则 */
export function createRule(data: any) {
  return client.post('/alerts/rules', data)
}

/** 告警日志 */
export function getLogs(isoWeek?: string) {
  return client.get('/alerts/logs', { params: { iso_week: isoWeek } })
}
