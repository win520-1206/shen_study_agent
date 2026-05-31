import { reactive } from 'vue'
import type { ProfileBuildResponse } from './types'

export const appState = reactive({
  studentId: 0,
  studentName: '',
  result: null as ProfileBuildResponse | null,
  loading: false,
  error: '',
  streamMode: false,
  demoMode: true,
  refreshKey: 0,
})
