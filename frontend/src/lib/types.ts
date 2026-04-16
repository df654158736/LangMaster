export interface KnowledgePointBrief {
  id: number;
  title: string;
  category: string;
  level: string;
  interview_heat: number;
  dev_utility: number;
  scenario: string;
  tags: string[];
  sort_order: number;
}

export interface KnowledgePoint extends KnowledgePointBrief {
  code_example: string;
  key_points: string[];
  common_mistakes: string[];
  related_point_ids: number[];
}

export interface UserProgress {
  point_id: number;
  mastery: "not_started" | "partial" | "mastered";
  last_reviewed_at: string | null;
  review_count: number;
  is_favorite: boolean;
}

export interface InterviewConfig {
  categories?: string[];
  levels?: string[];
  min_heat?: number;
  count: number;
  strategy: "smart" | "random" | "sequential";
}

export interface InterviewStartResult {
  session_id: number;
  questions: KnowledgePoint[];
}

export interface InterviewReport {
  id: number;
  config: Record<string, unknown>;
  results: { point_id: number; self_score: string }[];
  total_mastered: number;
  total_partial: number;
  total_unfamiliar: number;
  created_at: string;
}

export interface DashboardStats {
  total_points: number;
  mastered_count: number;
  interview_count: number;
  weak_count: number;
  last_score_percent: number | null;
}

export interface WeakPoint {
  point_id: number;
  title: string;
  mastery: string;
  category: string;
  level: string;
}
