import { reactive } from 'vue'
import type { ProfileBuildResponse } from './types'

const STORAGE_KEY = 'learnmate_student'

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const { studentId, studentName } = JSON.parse(raw)
      return { studentId: studentId || 0, studentName: studentName || '' }
    }
  } catch { /* ignore */ }
  return { studentId: 0, studentName: '' }
}

const saved = loadFromStorage()

export const appState = reactive({
  studentId: saved.studentId,
  studentName: saved.studentName,
  result: null as ProfileBuildResponse | null,
  loading: false,
  error: '',
  streamMode: false,
  demoMode: true,
  refreshKey: 0,
})

export function persistStudent(id: number, name: string) {
  appState.studentId = id
  appState.studentName = name
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ studentId: id, studentName: name }))
}

export function clearStudent() {
  appState.studentId = 0
  appState.studentName = ''
  appState.result = null
  localStorage.removeItem(STORAGE_KEY)
}
