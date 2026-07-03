import client from './client'

/** AI 分析 */
export function analyze(type: string, warehouseCodes: string[], isoWeek: string) {
  return client.post('/ai/analyze', {
    type,
    warehouse_codes: warehouseCodes,
    iso_week: isoWeek,
  })
}
