import client from './client'

/** 多仓对比 */
export function compare(warehouseCodes: string[], isoWeek: string, metric: string) {
  return client.post('/comparison', {
    warehouse_codes: warehouseCodes,
    iso_week: isoWeek,
    metric,
  })
}

/** 多仓对比（GET 方式，兼容后端） */
export function getComparison(warehouseCodes: string[], isoWeek: string, metric: string) {
  return client.get('/comparison', {
    params: {
      warehouse_codes: warehouseCodes.join(','),
      iso_week: isoWeek,
      metric,
    },
  })
}
