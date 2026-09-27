export interface UploadResult {
  share_id: string;
  share_url: string;
  expires_at: string;
}

export interface ShareInfo {
  filename: string;
  size: number;
  expires_at: string;
  password_required: boolean;
}

interface DownloadResult {
  url: string;
}

// FastAPI sends `detail` as a string for our own errors and as a list for validation errors.
interface ErrorBody {
  detail?: string | { loc: (string | number)[]; msg: string }[];
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, options);
  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(errorMessage(body) ?? `Request failed (${response.status})`);
  }
  return body as T;
}

function errorMessage(body: ErrorBody | null): string | null {
  const detail = body?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((error) => `${error.loc.at(-1)}: ${error.msg}`).join(", ");
  }
  return null;
}

export function messageOf(error: unknown): string {
  return error instanceof Error ? error.message : "Something went wrong";
}

export function uploadFile(formData: FormData) {
  return request<UploadResult>("/api/files", { method: "POST", body: formData });
}

export function getShare(shareId: string) {
  return request<ShareInfo>(`/api/share/${encodeURIComponent(shareId)}`);
}

export function requestDownload(shareId: string, password?: string) {
  return request<DownloadResult>(
    `/api/share/${encodeURIComponent(shareId)}/download`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: password || null }),
    },
  );
}
