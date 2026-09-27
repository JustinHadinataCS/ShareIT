# ShareIT 🔗

A small file-sharing app. Upload a file, get a link, send it to someone. The link dies after a set time or a set number of downloads, whichever comes first.

**Try it here: http://100.54.219.60/**

## What you can do

- Upload a file (up to 10 MB)
- Pick when the link expires: 5 minutes, 1 hour, 1 day, or 7 days
- Limit how many times it can be downloaded (1 to 50)
- Add a password if you want

## How it works

```
browser ──> EC2 (Docker: FastAPI + the built React app)
               ├── DynamoDB   one record per link
               └── S3         the files, fully private

browser <── S3 presigned URL, valid for 60 seconds
```

React talks to a FastAPI backend, which runs in a single Docker container on EC2. It also serves the frontend. Files go into a private S3 bucket, and each link is a row in DynamoDB. When you hit download, the backend checks the link and hands back an S3 URL that only works for 60 seconds.

Built with React + Vite, FastAPI, Pydantic, boto3, S3, DynamoDB, EC2, Docker and GitHub Actions.

## Security bits I cared about

- **The bucket is never public.** The only way to a file is a presigned URL, and only after the link passes every check.
- **No AWS keys on the server.** The EC2 instance has an IAM role that can only put/get objects in one bucket and read/update one table.
- **Link IDs can't be guessed.** They come from `secrets.token_urlsafe(16)`.
- **Passwords are hashed with Argon2.** A wrong guess doesn't use up a download.
- **The download count can't be double-spent.** It's decremented with a conditional update, so if two people race for the last download, only one gets it.
- **Old stuff cleans itself up.** DynamoDB TTL removes expired links, and an S3 lifecycle rule deletes files after 7 days. The code still checks expiry itself, since TTL can lag.
- **Every endpoint is rate-limited per IP.** 10 uploads a minute, 60 link lookups, and 10 download attempts, which also caps password guessing.

Still on the to-do list: HTTPS.

## Running it locally

You'll need an S3 bucket, a DynamoDB table (partition key `share_id`), and AWS credentials that can reach them.

```bash
# backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # then fill in your region, bucket and table
uvicorn app.main:app --reload
```

```bash
# frontend (in a second terminal)
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173. Vite forwards `/api` calls to the backend, so there's no CORS setup.

## Tests

```bash
cd backend
pytest
```

The tests use [moto](https://github.com/getmoto/moto) to fake S3 and DynamoDB, so they never touch real AWS. GitHub Actions runs them on every push, along with a frontend lint and build.

## Deploying

On an EC2 instance with Docker and the IAM role attached:

```bash
git clone https://github.com/JustinHadinataCS/ShareIT.git && cd ShareIT
nano .env    # AWS_REGION, S3_BUCKET, DYNAMODB_TABLE, PUBLIC_URL (no keys!)
docker build -t shareit .
docker run -d -p 80:8000 --env-file .env --restart unless-stopped --name shareit shareit
```
