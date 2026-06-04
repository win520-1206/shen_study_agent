import axios from 'axios'
import type {
  StudentResponse,
  ProfileBuildResponse,
  QAResponse,
  AssessmentHistoryResponse,
  DashboardResponse,
  OverviewSummaryResponse,
  KnowledgeGraphData,
  QuizGradeResponse,
} from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000,
})

export async function createStudent(
  name: string,
  major: string,
): Promise<StudentResponse> {
  const { data } = await api.post<StudentResponse>('/students', {
    name,
    major,
    target_course: '机器学习基础',
  })
  return data
}

export async function buildProfile(
  studentId: number,
  message: string,
): Promise<ProfileBuildResponse> {
  const { data } = await api.post<ProfileBuildResponse>('/chat/profile-build', {
    student_id: studentId,
    message,
  })
  return data
}

export async function askQuestion(
  studentId: number,
  question: string,
  socratic: boolean = false,
): Promise<QAResponse> {
  const { data } = await api.post<QAResponse>('/chat/qa', {
    student_id: studentId,
    question,
    socratic,
  })
  return data
}

export async function getAssessments(
  studentId: number,
): Promise<AssessmentHistoryResponse> {
  const { data } = await api.get<AssessmentHistoryResponse>(
    `/student/${studentId}/assessments`,
  )
  return data
}

export async function getDashboard(
  studentId: number,
): Promise<DashboardResponse> {
  const { data } = await api.get<DashboardResponse>(`/student/${studentId}/dashboard`)
  return data
}

export async function getOverviewSummary(): Promise<OverviewSummaryResponse> {
  const { data } = await api.get<OverviewSummaryResponse>('/overview/summary')
  return data
}

export async function getKnowledgeGraph(): Promise<KnowledgeGraphData> {
  const { data } = await api.get<KnowledgeGraphData>('/kb/graph')
  return data
}



export async function gradeQuiz(
  studentId: number,
  question: string,
  studentAnswer: string,
  referenceAnswer: string,
  knowledgeUnit: string,
): Promise<QuizGradeResponse> {
  const { data } = await api.post<QuizGradeResponse>('/quiz/grade', {
    student_id: studentId,
    question,
    student_answer: studentAnswer,
    reference_answer: referenceAnswer,
    knowledge_unit: knowledgeUnit,
  })
  return data
}
export interface StreamCallbacks {
  onProfile?: (data: any) => void
  onDiagnosis?: (data: any) => void
  onTraces?: (data: any) => void
  onResource?: (data: any) => void
  onPlan?: (data: any) => void
  onDone?: () => void
  onError?: (msg: string) => void
}

export async function buildProfileStream(
  studentId: number,
  message: string,
  callbacks: StreamCallbacks,
): Promise<void> {
  const resp = await fetch(`/api/v1/chat/profile-build/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ student_id: studentId, message }),
  })
  if (!resp.ok) {
    callbacks.onError?.(`HTTP ${resp.status}`)
    return
  }
  const reader = resp.body?.getReader()
  if (!reader) { callbacks.onError?.('No stream body'); return }
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''
    let currentEvent = ''
    for (const line of lines) {
      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7).trim()
      } else if (line.startsWith('data: ')) {
        const jsonStr = line.slice(6)
        try {
          const data = JSON.parse(jsonStr)
          if (currentEvent === 'profile') callbacks.onProfile?.(data)
          else if (currentEvent === 'diagnosis') callbacks.onDiagnosis?.(data)
          else if (currentEvent === 'traces') callbacks.onTraces?.(data)
          else if (currentEvent === 'resource') callbacks.onResource?.(data)
          else if (currentEvent === 'plan') callbacks.onPlan?.(data)
          else if (currentEvent === 'done') callbacks.onDone?.()
          else if (currentEvent === 'error') callbacks.onError?.(data.detail || 'Unknown error')
        } catch { /* skip malformed */ }
      }
    }
  }
}
