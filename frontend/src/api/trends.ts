import client from './client'

/** 获取某仓库某周的趋势数据（表格 + 图表） */
export function getTrend(warehouseCode: string, isoWeek: string) {
  return client.get(`/trends/${warehouseCode}`, { params: { iso_week: isoWeek } })
}

/** 获取某仓库某周的图表数据（三曲线） */
export function getChartData(warehouseCode: string, isoWeek: string) {
  return client.get(`/trends/${warehouseCode}/chart`, { params: { iso_week: isoWeek } })
}
