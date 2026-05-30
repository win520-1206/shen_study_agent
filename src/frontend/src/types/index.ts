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
  decision_reason: string
  impact_on_result: string
}

export interface StudyPlan {
  stage: string
  objectives: string[]
  recommended_resources: string[]
  practice_task: string
  rationale: string
}

export interface CredibilityInfo {
  based_on_kb: boolean
  reviewed: boolean
  source_modules: string[]
  note: string
}

export interface ProfileBuildResponse {
  student: StudentResponse
  diagnosis: Record<string, any>
  resources: ResourceCard[]
  study_plan: StudyPlan[]
  traces: TraceCard[]
  recommendation_summary: string
  credibility: CredibilityInfo | null
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
  improvement_points: WeakPoint[]
  trend: Record<string, string>
  progress_summary: string
}

export interface DashboardResponse {
  student: StudentResponse
  latest_diagnosis: Record<string, any>
  latest_plan: StudyPlan[]
  resources: ResourceCard[]
  recent_assessments: Array<{
    knowledge_unit: string
    score: number
    feedback: string
    next_recommendation: string
    trend: string
  }>
  traces: TraceCard[]
  recommendation_summary: string
  progress_summary: string
  weak_point_rank: WeakPoint[]
  improvement_rank: WeakPoint[]
  updated_at: string
}

export interface OverviewSummaryResponse {
  student_count: number
  active_session_count: number
  most_common_weak_points: Array<{
    knowledge_unit: string
    count: number
  }>
  resource_type_stats: Array<{
    resource_type: string
    count: number
  }>
  average_score: number
  score_band_distribution: Array<{
    label: string
    count: number
  }>
  featured_students: Array<{
    name: string
    major: string
    goal: string
    weak_points: string[]
  }>
}
