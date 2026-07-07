import client from './client'

export function getWebhooks() {
  return client.get('/webhooks')
}

export function createWebhook(data: { warehouse_id: number; webhook_url: string; notify_users?: string }) {
  return client.post('/webhooks', data)
}

export function updateWebhook(id: number, data: { webhook_url?: string; notify_users?: string; is_active?: boolean }) {
  return client.put(`/webhooks/${id}`, data)
}

export function deleteWebhook(id: number) {
  return client.delete(`/webhooks/${id}`)
}

export function pushChart(data: { warehouse_code: string; iso_week: string; chart_base64: string }) {
  return client.post('/webhooks/push', data)
}

export function pushAll(data: { iso_week: string }) {
  return client.post('/webhooks/push-all', data)
}
