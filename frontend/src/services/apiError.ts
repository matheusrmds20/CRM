interface ApiErrorResponse {
  response?: {
    status?: number;
    data?: {
      detail?: unknown;
    };
  };
}

function isApiError(value: unknown): value is ApiErrorResponse {
  return typeof value === 'object' && value !== null && 'response' in value;
}

export function getApiErrorStatus(err: unknown): number | undefined {
  return isApiError(err) ? err.response?.status : undefined;
}

export function getApiErrorMessage(err: unknown, fallback: string): string {
  if (!isApiError(err)) return fallback;
  const detail = err.response?.data?.detail;
  if (typeof detail === 'string' && detail.length > 0) return detail;
  if (Array.isArray(detail) && typeof detail[0]?.msg === 'string') return detail[0].msg;
  return fallback;
}