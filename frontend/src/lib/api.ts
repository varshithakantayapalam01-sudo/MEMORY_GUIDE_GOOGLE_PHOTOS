export interface APIResponse<T = any> {
  success: boolean;
  data: T | null;
  error?: {
    code: string;
    message: string;
    details?: any;
  } | null;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface QuestionData {
  questionId: string;
  round: number;
  text: string;
  options: string[];
  dimensionTested: string;
  subattributeKey?: string;
}

export interface ProgressData {
  activeCandidates: number;
  reserveCandidates: number;
  round: number;
}

export interface SelectionMetadata {
  dimension: string;
  subattributeKey?: string;
  value?: string;
  discriminationScore: number;
  memorabilityWeight: number;
  finalScore: number;
  distribution?: Record<string, number>;
}

export interface CandidateData {
  imageId: string;
  rank: number;
  score: number;
  semanticScore: number;
  structuredScore: number;
  imageUrl: string;
}

export interface FoundSummary {
  totalRounds: number;
  totalIdkCount: number;
  questionsAsked: string[];
  candidateNarrowingPath: string;
}

export interface StepResponseData {
  action: 'ask_question' | 'show_candidates' | 'found';
  question?: QuestionData;
  candidates?: CandidateData[];
  progress?: ProgressData;
  selectionMetadata?: SelectionMetadata;
  selectedImageId?: string;
  summary?: FoundSummary;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://memoryguidegooglephotos-production.up.railway.app/api/v1';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errMessage = `HTTP Error ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.error?.message) {
        errMessage = errJson.error.message;
      }
    } catch (_) {}
    throw new Error(errMessage);
  }
  return response.json();
}

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/health`, { cache: 'no-store' });
  return handleResponse<HealthResponse>(res);
}

export async function createSession(mode: 'demo' | 'research'): Promise<APIResponse<{ sessionId: string; mode: string; status: string }>> {
  const res = await fetch(`${API_BASE_URL}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode }),
  });
  return handleResponse(res);
}

export async function uploadPhotos(sessionId: string, files: File[]): Promise<APIResponse<{ uploadedCount: number; imageCount: number; status: string; message: string }>> {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/upload`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(res);
}

export async function submitQuery(sessionId: string, query: string): Promise<APIResponse<StepResponseData>> {
  const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  return handleResponse(res);
}

export async function submitAnswer(sessionId: string, answerText: string): Promise<APIResponse<StepResponseData>> {
  const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answerText }),
  });
  return handleResponse(res);
}

export async function selectCandidate(
  sessionId: string,
  payload: { selectionType: 'found' | 'close' | 'none'; imageId?: string; rejectedImageIds?: string[] }
): Promise<APIResponse<StepResponseData>> {
  const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/select`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function submitFeedback(
  sessionId: string,
  payload: { helpfulnessRating: number; confusingFeedback?: string }
): Promise<APIResponse<{ recorded: boolean }>> {
  const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}
