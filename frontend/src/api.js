async function request(path, options) {
  const response = await fetch(path, options);
  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(errorMessage(body) ?? `Request failed (${response.status})`);
  }
  return body;
}

// FastAPI sends `detail` as a string for our own errors and as a list for validation errors.
function errorMessage(body) {
  const detail = body?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((error) => `${error.loc.at(-1)}: ${error.msg}`).join(", ");
  }
  return null;
}

export function uploadFile(formData) {
  return request("/api/files", { method: "POST", body: formData });
}
