<template>
  <el-card>
    <el-button type="primary" @click="showDialog = true">新建用户</el-button>
    <el-table :data="users" border stripe style="margin-top: 12px">
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="role" label="角色" />
      <el-table-column prop="is_active" label="状态">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" title="新建用户" width="480px">
      <el-form label-width="80px">
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="Admin" value="admin" />
            <el-option label="Global Viewer" value="global_viewer" />
            <el-option label="Viewer" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">{{ t('create') }}</el-button>
      </template>
    </el-dialog>

    <PageIntro :items="[
      '管理员可创建新用户并分配角色（管理员、仓库查看员、全局查看员）',
      '仓库查看员仅能查看分配给自己的仓库数据',
      '全局查看员可查看所有仓库数据但不能上传或管理',
      '点击编辑可修改用户信息和仓库绑定'
    ]" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { getUsers, createUser } from '../api/users'
import PageIntro from '../components/PageIntro.vue'
import { ElMessage } from 'element-plus'

const { t } = useI18n()
const users = ref<any[]>([])
const showDialog = ref(false)
const creating = ref(false)
const form = reactive({
  username: '',
  password: '',
  role: 'viewer',
  warehouse_ids: [] as number[],
})

onMounted(loadUsers)

async function loadUsers() {
  try {
    const resp: any = await getUsers()
    users.value = resp.data
  } catch {
    /* 忽略 */
  }
}

async function handleCreate() {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  creating.value = true
  try {
    await createUser(form)
    ElMessage.success('创建成功')
    showDialog.value = false
    form.username = ''
    form.password = ''
    form.role = 'viewer'
    await loadUsers()
  } catch (err: any) {
    ElMessage.error(err?.message || '创建失败')
  } finally {
    creating.value = false
  }
}
</script>
