/**
 * API request/response types. No `any`; strict typing for props and API.
 * Mirrors the Pydantic schemas defined in the FastAPI backend.
 */

export interface UploadResponse {
  status: string;
  filename: string;
  chunks: number;
}

export interface QueryRequest {
  query: string;
}

export interface SourceDoc {
  text: string;
  score?: number | null;
  metadata?: Record<string, unknown> | null;
}

export interface QueryResponse {
  answer: string;
  sources: SourceDoc[];
}

export interface ApiErrorDetail {
  detail?: string | string[];
}

export function getErrorMessage(err: unknown): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const res = (err as { response?: { data?: ApiErrorDetail } }).response;
    const d = res?.data?.detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) return d.map(String).join(', ');
  }
  if (err instanceof Error) return err.message;
  return 'An unexpected error occurred.';
}

export function isTimeoutError(err: unknown): boolean {
  if (err && typeof err === 'object' && 'code' in err) {
    return (err as { code?: string }).code === 'ECONNABORTED';
  }
  return false;
}
