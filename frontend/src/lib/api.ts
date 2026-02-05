/**
 * Centralized API client: base URL, 60s timeouts.
 * Prevents infinite loading when backend hangs (e.g. model download).
 * Uses relative /api paths which are proxied in dev via vite.config.ts
 */
import axios from 'axios';
import type { QueryRequest, QueryResponse, UploadResponse } from '../types/api';

// In development, use relative /api path (proxied to backend)
// In production, use absolute URL from env or current origin
const BASE_URL = import.meta.env.PROD 
  ? (import.meta.env.VITE_API_URL || `${window.location.origin}`)
  : '';

export const TIMEOUT_MS = 60_000;

const client = axios.create({
  baseURL: BASE_URL,
  timeout: TIMEOUT_MS,
});

export async function uploadPdf(
  file: File,
  options?: { onProgress?: (percent: number) => void }
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  // NOTE: Do NOT set Content-Type header; axios will auto-set with correct boundary
  const { data } = await client.post<UploadResponse>('/api/upload', formData, {
    timeout: TIMEOUT_MS,
    onUploadProgress: options?.onProgress
      ? (event) => {
          if (event.total) {
            const percent = Math.round((event.loaded / event.total) * 100);
            if (options.onProgress) {
              options.onProgress(percent);
            }
          }
        }
      : undefined,
  });
  return data;
}

export async function queryDocuments(
  payload: QueryRequest
): Promise<QueryResponse> {
  const { data } = await client.post<QueryResponse>('/api/query', payload, {
    headers: { 'Content-Type': 'application/json' },
    timeout: TIMEOUT_MS,
  });
  return data;
}
