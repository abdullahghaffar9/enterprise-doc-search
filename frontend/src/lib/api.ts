/**
 * Centralized API client: base URL, 60s timeouts.
 * Prevents infinite loading when backend hangs (e.g. model download).
 */
import axios from 'axios';
import type { QueryRequest, QueryResponse, UploadResponse } from '../types/api';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export const TIMEOUT_MS = 60_000;

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: TIMEOUT_MS,
});

export async function uploadPdf(
  file: File,
  options?: { onProgress?: (percent: number) => void }
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await client.post<UploadResponse>('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: TIMEOUT_MS,
    onUploadProgress: options?.onProgress
      ? (event: ProgressEvent) => {
          if (event.total) {
            const percent = Math.round((event.loaded / event.total) * 100);
            options.onProgress(percent);
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
    timeout: TIMEOUT_MS,
  });
  return data;
}
