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
    <section>
      <h1>Download a file</h1>
      <p>Share ID: {shareId}</p>

      <dl>
        <dt>File name</dt>
        <dd>{share.filename}</dd>

        <dt>Size</dt>
        <dd>{(share.size / 1024 / 1024).toFixed(1)} MB</dd>

        <dt>Expires</dt>
        <dd>
          <time dateTime={share.expiresAt}>
            {new Date(share.expiresAt).toLocaleString()}
          </time>
        </dd>
      </dl>

      <form onSubmit={handleSubmit}>
        {share.passwordRequired && (
          <div>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
            />
          </div>
        )}

        <button type="submit">Download</button>
      </form>
    </section>
  );
}

export default SharePage;
