export interface StudentProfile {
  major_background: string
  learning_goal: string
  prerequisite_level: string
  weak_points: string[]
  learning_style: string
  weekly_hours: string
  exercise_preference: string
  target_outcome: string
}

export interface StudentResponse {
  id: number
  name: string
  major: string
  target_course: string
  profile: StudentProfile | null
}

export interface ResourceCard {
  resource_type: string
  title: string
  content: string
  source_refs: string[]
}

export interface TraceCard {
  agent_name: string
  input_summary: string
  output_summary: string
}

export interface StudyPlan {
  stage: string
  objectives: string[]
  recommended_resources: string[]
  practice_task: string
}

export interface ProfileBuildResponse {
  student: StudentResponse
  diagnosis: Record<string, any>
  resources: ResourceCard[]
  study_plan: StudyPlan[]
  traces: TraceCard[]
}

export interface QAResponse {
  answer: string
  source_refs: string[]
  agent_trace: TraceCard
}

export interface AssessmentRecordItem {
  knowledge_unit: string
  score: number
  feedback: string
  created_at: string | null
}

export interface WeakPoint {
  knowledge_unit: string
  avg_score: number
  attempts: number
}

export interface AssessmentHistoryResponse {
  records: AssessmentRecordItem[]
  weak_points: WeakPoint[]
  trend: Record<string, string>
}
