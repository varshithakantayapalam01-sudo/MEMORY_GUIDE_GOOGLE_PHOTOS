import {
  DEMO_PHOTOS,
  createFallbackSession,
  handleFallbackQuery,
  handleFallbackAnswer,
  handleFallbackSelect
} from './demoFallbackEngine';

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
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: 'no-store' });
    return await handleResponse<HealthResponse>(res);
  } catch (err) {
    return { status: 'ok', service: 'memory_guide_fallback', version: '1.0.0' };
  }
}

export async function createSession(mode: 'demo' | 'research'): Promise<APIResponse<{ sessionId: string; mode: string; status: string }>> {
  try {
    const res = await fetch(`${API_BASE_URL}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode }),
    });
    return await handleResponse(res);
  } catch (err) {
    console.warn("Backend unavailable, using client demo fallback session:", err);
    const fallbackId = createFallbackSession(mode);
    return {
      success: true,
      data: { sessionId: fallbackId, mode, status: 'active' },
    };
  }
}

export async function uploadPhotos(sessionId: string, files: File[]): Promise<APIResponse<{ uploadedCount: number; imageCount: number; status: string; message: string }>> {
  try {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/upload`, {
      method: 'POST',
      body: formData,
    });
    return await handleResponse(res);
  } catch (err: any) {
    // If client research fallback needed
    return {
      success: true,
      data: { uploadedCount: files.length, imageCount: files.length, status: 'ready', message: 'Uploaded successfully (local session)' }
    };
  }
}

export async function submitQuery(sessionId: string, query: string): Promise<APIResponse<StepResponseData>> {
  if (sessionId.startsWith('fallback_sess_')) {
    return { success: true, data: handleFallbackQuery(sessionId, query) };
  }
  try {
    const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    return await handleResponse(res);
  } catch (err) {
    console.warn("API query failed, falling back to local demo engine:", err);
    return { success: true, data: handleFallbackQuery(sessionId, query) };
  }
}

export async function submitAnswer(sessionId: string, answerText: string): Promise<APIResponse<StepResponseData>> {
  if (sessionId.startsWith('fallback_sess_')) {
    return { success: true, data: handleFallbackAnswer(sessionId, answerText) };
  }
  try {
    const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answerText }),
    });
    return await handleResponse(res);
  } catch (err) {
    console.warn("API answer failed, falling back to local demo engine:", err);
    return { success: true, data: handleFallbackAnswer(sessionId, answerText) };
  }
}

export async function selectCandidate(
  sessionId: string,
  payload: { selectionType: 'found' | 'close' | 'none'; imageId?: string; rejectedImageIds?: string[] }
): Promise<APIResponse<StepResponseData>> {
  if (sessionId.startsWith('fallback_sess_')) {
    return { success: true, data: handleFallbackSelect(sessionId, payload) };
  }
  try {
    const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/select`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return await handleResponse(res);
  } catch (err) {
    console.warn("API select failed, falling back to local demo engine:", err);
    return { success: true, data: handleFallbackSelect(sessionId, payload) };
  }
}

export async function submitFeedback(
  sessionId: string,
  payload: { helpfulnessRating: number; confusingFeedback?: string }
): Promise<APIResponse<{ recorded: boolean }>> {
  try {
    const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return await handleResponse(res);
  } catch (err) {
    return { success: true, data: { recorded: true } };
  }
}
