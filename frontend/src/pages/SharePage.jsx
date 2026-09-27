import Emoji from "../components/Emoji.jsx";

const PLACEHOLDER_SHARE = {
  filename: "example.pdf",
  size: 2_400_000,
  expiresAt: "2026-10-04T12:00:00Z",
  passwordRequired: true,
};

function SharePage({ shareId }) {
  const share = PLACEHOLDER_SHARE;

  function handleSubmit(event) {
    event.preventDefault();
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
        <dd>{(share.size / 1024 / 1024).toFixed(1)} MB</dd>

        <dt>
          <Emoji>⏳</Emoji> Expires
        </dt>
        <dd>
          <time dateTime={share.expiresAt}>
            {new Date(share.expiresAt).toLocaleString()}
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
        {share.passwordRequired && (
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

        <button type="submit">
          <Emoji>⬇️</Emoji> Download
        </button>
      </form>
    </section>
  );
}

export default SharePage;
