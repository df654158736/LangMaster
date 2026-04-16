import type {
  KnowledgePointBrief,
  KnowledgePoint,
  UserProgress,
  InterviewConfig,
  InterviewStartResult,
  InterviewReport,
  DashboardStats,
  WeakPoint,
} from "./types";
import { getUserId } from "./user";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-User-Id": getUserId(),
      ...options?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// Knowledge Points
export function getPoints(params?: {
  category?: string;
  level?: string;
  sort?: string;
}): Promise<KnowledgePointBrief[]> {
  const search = new URLSearchParams();
  if (params?.category) search.set("category", params.category);
  if (params?.level) search.set("level", params.level);
  if (params?.sort) search.set("sort", params.sort);
  const qs = search.toString();
  return fetchAPI(`/api/points${qs ? `?${qs}` : ""}`);
}

export function getPoint(id: number): Promise<KnowledgePoint> {
  return fetchAPI(`/api/points/${id}`);
}

// Progress
export function getProgress(): Promise<UserProgress[]> {
  return fetchAPI("/api/progress");
}

export function updateMastery(
  pointId: number,
  mastery: string
): Promise<UserProgress> {
  return fetchAPI(`/api/progress/${pointId}`, {
    method: "PUT",
    body: JSON.stringify({ mastery }),
  });
}

export function toggleFavorite(
  pointId: number,
  isFavorite: boolean
): Promise<UserProgress> {
  return fetchAPI(`/api/progress/${pointId}/favorite`, {
    method: "PUT",
    body: JSON.stringify({ is_favorite: isFavorite }),
  });
}

// Interview
export function startInterview(
  config: InterviewConfig
): Promise<InterviewStartResult> {
  return fetchAPI("/api/interview/start", {
    method: "POST",
    body: JSON.stringify(config),
  });
}

export function submitAnswer(
  sessionId: number,
  pointId: number,
  selfScore: string
): Promise<{ status: string; results_count: number }> {
  return fetchAPI(`/api/interview/${sessionId}/answer`, {
    method: "POST",
    body: JSON.stringify({ point_id: pointId, self_score: selfScore }),
  });
}

export function getReport(sessionId: number): Promise<InterviewReport> {
  return fetchAPI(`/api/interview/${sessionId}/report`);
}

export function getInterviewHistory(): Promise<InterviewReport[]> {
  return fetchAPI("/api/interview/history");
}

// Stats
export function getDashboardStats(): Promise<DashboardStats> {
  return fetchAPI("/api/stats/dashboard");
}

export function getWeakPoints(): Promise<WeakPoint[]> {
  return fetchAPI("/api/stats/weak-points");
}
