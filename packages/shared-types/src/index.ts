// ============================================================================
// Student Study Planner - Shared Types
// ============================================================================

// ----------------------------------------------------------------------------
// Input Types
// ----------------------------------------------------------------------------

export interface GeneratePlanInput {
  syllabus: string;
  todoList: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  studyHoursPerDay?: number;
  preferredTimeSlots?: TimeSlot[];
  breakDuration?: number;
  weekendStudy?: boolean;
}

export type TimeSlot = 'morning' | 'afternoon' | 'evening' | 'night';

// ----------------------------------------------------------------------------
// Router Types
// ----------------------------------------------------------------------------

export type Difficulty = 'easy' | 'hard';

export interface RouterOutput {
  difficulty: Difficulty;
  reasoning: string;
}

// ----------------------------------------------------------------------------
// Study Plan Types
// ----------------------------------------------------------------------------

export interface StudySession {
  startTime: string;  // HH:MM format
  endTime: string;    // HH:MM format
  subject: string;
  topic: string;
  activityType: 'study' | 'review' | 'practice' | 'break';
  description?: string;
}

export interface DailySchedule {
  date: string;  // YYYY-MM-DD format
  dayOfWeek: string;
  sessions: StudySession[];
  notes?: string;
}

export interface Subject {
  name: string;
  totalHours: number;
  priority: 'high' | 'medium' | 'low';
  topics: string[];
  deadlines?: SubjectDeadline[];
}

export interface SubjectDeadline {
  topic: string;
  dueDate: string;  // YYYY-MM-DD
  type: 'exam' | 'assignment' | 'project' | 'quiz';
}

export interface Milestone {
  date: string;  // YYYY-MM-DD
  title: string;
  description: string;
  subjects: string[];
  completed?: boolean;
}

export interface StudyPlan {
  id?: string;
  title: string;
  summary: string;
  startDate: string;  // YYYY-MM-DD
  endDate: string;    // YYYY-MM-DD
  subjects: Subject[];
  dailySchedules: DailySchedule[];
  milestones: Milestone[];
  weeklyHours: number;
  tips: string[];
  createdAt?: string;
  updatedAt?: string;
}

// ----------------------------------------------------------------------------
// API Response Types
// ----------------------------------------------------------------------------

export interface GeneratePlanResponse {
  success: boolean;
  planId: string;
  plan: StudyPlan;
  htmlContent: string;
  difficulty: Difficulty;
  processingTime: number;  // milliseconds
}

export interface ErrorResponse {
  success: false;
  error: string;
  code: string;
  details?: Record<string, unknown>;
}

export interface SavePlanResponse {
  success: boolean;
  planId: string;
  savedAt: string;
}

export interface FeedbackRequest {
  planId: string;
  action: 'regenerate' | 'save' | 'share' | 'rate';
  rating?: number;  // 1-5
  comment?: string;
}

export interface FeedbackResponse {
  success: boolean;
  feedbackId: string;
}

// ----------------------------------------------------------------------------
// Validation Types
// ----------------------------------------------------------------------------

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
  suggestion?: string;
}

// ----------------------------------------------------------------------------
// Security Types
// ----------------------------------------------------------------------------

export interface InputGuardResult {
  isSafe: boolean;
  blockedPatterns: string[];
  sanitizedInput?: string;
}

export interface OutputGuardResult {
  isValid: boolean;
  parsedPlan?: StudyPlan;
  fixedFields: string[];
  errors: string[];
}

// ----------------------------------------------------------------------------
// LangSmith Types
// ----------------------------------------------------------------------------

export interface PromptVersion {
  id: string;
  name: string;
  version: string;
  template: string;
  createdAt: string;
  metadata?: Record<string, unknown>;
}

export interface TraceMetadata {
  userId?: string;
  sessionId: string;
  difficulty: Difficulty;
  inputLength: number;
  processingTime: number;
}
