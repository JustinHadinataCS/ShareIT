import { useState } from "react";
import { uploadFile } from "../api.js";

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const EXPIRY_OPTIONS = [
  { label: "5 minutes", seconds: 5 * 60 },
  { label: "1 hour", seconds: 60 * 60 },
  { label: "1 day", seconds: 24 * 60 * 60 },
  { label: "7 days", seconds: 7 * 24 * 60 * 60 },
];

function UploadPage() {
  const [share, setShare] = useState(null);
  const [error, setError] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    setShare(null);
    if (formData.get("file").size > MAX_FILE_SIZE) {
      setError("File is larger than 10 MB");
      return;
    }

    setError(null);
    setIsUploading(true);
    try {
      setShare(await uploadFile(formData));
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section>
      <h1>Share a file</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="file">File (max 10 MB)</label>
          <input id="file" name="file" type="file" required />
        </div>

        <div>
          <label htmlFor="expires_in">Expires after</label>
          <select id="expires_in" name="expires_in" defaultValue={24 * 60 * 60}>
            {EXPIRY_OPTIONS.map((option) => (
              <option key={option.seconds} value={option.seconds}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="max_downloads">Max downloads (1–50)</label>
          <input
            id="max_downloads"
            name="max_downloads"
            type="number"
            min="1"
            max="50"
            defaultValue="1"
            required
          />
        </div>

        <div>
          <label htmlFor="password">Password (optional)</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
          />
        </div>

        <button type="submit" disabled={isUploading}>
          {isUploading ? "Uploading..." : "Upload"}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      {share && (
        <section>
          <h2>Your share link</h2>
          <p>
            <a href={share.share_url}>{share.share_url}</a>
          </p>
          <p>
            Expires{" "}
            <time dateTime={share.expires_at}>
              {new Date(share.expires_at).toLocaleString()}
            </time>
          </p>
        </section>
      )}
    </section>
  );
}

export default UploadPage;
