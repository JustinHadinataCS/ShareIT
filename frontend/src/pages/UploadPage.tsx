import { useState, type SubmitEvent } from "react";
import { messageOf, uploadFile, type UploadResult } from "../api.ts";
import Emoji from "../components/Emoji.tsx";

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const EXPIRY_OPTIONS = [
  { label: "5 minutes", seconds: 5 * 60 },
  { label: "1 hour", seconds: 60 * 60 },
  { label: "1 day", seconds: 24 * 60 * 60 },
  { label: "7 days", seconds: 7 * 24 * 60 * 60 },
];

function UploadPage() {
  const [share, setShare] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const file = formData.get("file");

    setShare(null);
    if (file instanceof File && file.size > MAX_FILE_SIZE) {
      setError("File is larger than 10 MB");
      return;
    }

    setError(null);
    setIsUploading(true);
    try {
      setShare(await uploadFile(formData));
    } catch (err) {
      setError(messageOf(err));
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="card">
      <h1>
        <Emoji>📤</Emoji> Share a file
      </h1>
      <p className="subtitle">Get a private link that expires on its own.</p>

      <form onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="file">
            <Emoji>📄</Emoji> File
          </label>
          <input
            id="file"
            name="file"
            type="file"
            required
            aria-describedby="file-hint"
          />
          <small id="file-hint" className="hint">
            Max 10 MB
          </small>
        </div>

        <div className="field">
          <label htmlFor="expires_in">
            <Emoji>⏳</Emoji> Expires after
          </label>
          <select id="expires_in" name="expires_in" defaultValue={24 * 60 * 60}>
            {EXPIRY_OPTIONS.map((option) => (
              <option key={option.seconds} value={option.seconds}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="max_downloads">
            <Emoji>🔢</Emoji> Max downloads
          </label>
          <input
            id="max_downloads"
            name="max_downloads"
            type="number"
            min="1"
            max="50"
            defaultValue="1"
            required
            aria-describedby="max-downloads-hint"
          />
          <small id="max-downloads-hint" className="hint">
            Between 1 and 50
          </small>
        </div>

        <div className="field">
          <label htmlFor="password">
            <Emoji>🔒</Emoji> Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            aria-describedby="password-hint"
          />
          <small id="password-hint" className="hint">
            Optional. Anyone downloading will need it.
          </small>
        </div>

        <button type="submit" disabled={isUploading}>
          <Emoji>{isUploading ? "⏳" : "🚀"}</Emoji>{" "}
          {isUploading ? "Uploading..." : "Upload"}
        </button>
      </form>

      {error && (
        <p className="alert" role="alert">
          <Emoji>⚠️</Emoji> {error}
        </p>
      )}

      {share && (
        <section className="result">
          <h2>
            <Emoji>✅</Emoji> Your share link
          </h2>
          <a className="share-link" href={share.share_url}>
            {share.share_url}
          </a>
          <p className="hint">
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
