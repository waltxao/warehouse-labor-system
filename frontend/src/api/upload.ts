import client from './client'

/** 上传 Excel 文件 */
export function uploadExcel(file: File, forceOverwrite = false) {
  const form = new FormData()
  form.append('file', file)
  return client.post(`/upload?force_overwrite=${forceOverwrite}`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** 获取上传日志 */
export function getUploadLogs() {
  return client.get('/upload/logs')
}
