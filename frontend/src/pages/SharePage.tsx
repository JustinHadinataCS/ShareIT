import { useEffect, useState, type SubmitEvent } from "react";
import {
  getShare,
  messageOf,
  requestDownload,
  type ShareInfo,
} from "../api.ts";
import Emoji from "../components/Emoji.tsx";

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

interface SharePageProps {
  shareId: string;
}

function SharePage({ shareId }: SharePageProps) {
  const [share, setShare] = useState<ShareInfo | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);

  useEffect(() => {
    let ignore = false;
    getShare(shareId).then(
      (data) => {
        if (!ignore) setShare(data);
      },
      (err: unknown) => {
        if (!ignore) setLoadError(messageOf(err));
      },
    );
    return () => {
      ignore = true;
    };
  }, [shareId]);

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    const password = new FormData(event.currentTarget).get("password")?.toString();

    setError(null);
    setHasStarted(false);
    setIsDownloading(true);
    try {
      const { url } = await requestDownload(shareId, password);
      window.location.assign(url);
      setHasStarted(true);
    } catch (err) {
      setError(messageOf(err));
    } finally {
      setIsDownloading(false);
    }
  }

  if (loadError) {
    return (
      <section className="card">
        <h1>
          <Emoji>🚫</Emoji> Link unavailable
        </h1>
        <p className="subtitle">{loadError}</p>
        <a className="button" href="/">
          <Emoji>📤</Emoji> Share your own file
        </a>
      </section>
    );
  }

  if (!share) {
    return (
      <section className="card">
        <p className="subtitle" role="status">
          <Emoji>⏳</Emoji> Loading...
        </p>
      </section>
    );
  }

  return (
    <section className="card">
      <h1>
        <Emoji>📥</Emoji> Download a file
      </h1>
      <p className="subtitle">Someone shared a file with you.</p>

      <dl className="details">
        <dt>
          <Emoji>📄</Emoji> File
        </dt>
        <dd>{share.filename}</dd>

        <dt>
          <Emoji>📦</Emoji> Size
        </dt>
        <dd>{formatSize(share.size)}</dd>

        <dt>
          <Emoji>⏳</Emoji> Expires
        </dt>
        <dd>
          <time dateTime={share.expires_at}>
            {new Date(share.expires_at).toLocaleString()}
          </time>
        </dd>

        <dt>
          <Emoji>🆔</Emoji> Link ID
        </dt>
        <dd>
          <code>{shareId}</code>
        </dd>
      </dl>

      <form onSubmit={handleSubmit}>
        {share.password_required && (
          <div className="field">
            <label htmlFor="password">
              <Emoji>🔒</Emoji> Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="off"
              required
              aria-describedby="password-hint"
            />
            <small id="password-hint" className="hint">
              The sender protected this file with a password.
            </small>
          </div>
        )}

        <button type="submit" disabled={isDownloading}>
          <Emoji>{isDownloading ? "⏳" : "⬇️"}</Emoji>{" "}
          {isDownloading ? "Preparing..." : "Download"}
        </button>
      </form>

      {error && (
        <p className="alert" role="alert">
          <Emoji>⚠️</Emoji> {error}
        </p>
      )}

      {hasStarted && (
        <p className="alert" role="status">
          <Emoji>✅</Emoji> Your download has started.
        </p>
      )}
    </section>
  );
}

export default SharePage;
