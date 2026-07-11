import client from './client'

export function getWebhooks() {
  return client.get('/webhooks')
}

export function createWebhook(data: {
  warehouse_id: number
  webhook_url: string
  notify_users?: string
  is_active?: boolean
  message_template?: string
  schedule_enabled?: boolean
  schedule_day?: number
  schedule_time?: string
}) {
  return client.post('/webhooks', data)
}

export function updateWebhook(id: number, data: {
  webhook_url?: string
  notify_users?: string
  is_active?: boolean
  message_template?: string
  schedule_enabled?: boolean
  schedule_day?: number
  schedule_time?: string
}) {
  return client.put(`/webhooks/${id}`, data)
}

export function deleteWebhook(id: number) {
  return client.delete(`/webhooks/${id}`)
}

export function pushAll(data: { iso_week: string; warehouse_codes: string[] }) {
  return client.post('/webhooks/push-all', data)
}
