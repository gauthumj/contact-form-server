# form-webhook

A small FastAPI service that receives contact form submissions and forwards them to a configured webhook (Discord/Telegram or any incoming webhook URL). The app is defined in `main.py`.

## Features
- Receives POST requests at `/api/contact` with `name`, `email`, and `message`.
- Forwards the payload to an upstream webhook using `httpx`.
- Simple Docker image provided for easy deployment.

## Requirements
- Python 3.11+
- (Optional) Docker

Install Python deps:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1  #optional
pip install -r requirements.txt
```

## Environment
The application requires a webhook URL to forward incoming messages. Set the `WEBHOOK_URL` environment variable or put it in a `.env` file (the app uses `python-dotenv`):

```
WEBHOOK_URL=https://your-webhook-url.example
PORT=4000  # optional, defaults to 4000 in the image
```

## Run locally
Start the server with Uvicorn:

```powershell
uvicorn main:app --host 0.0.0.0 --port 4000 --reload
```

## Run with Docker
Build the image (if your Dockerfile is named `dockerfile`, include `-f dockerfile`):

```powershell
# if Dockerfile is named Dockerfile
docker build -t contact-form-server .

# if file is named "dockerfile"
docker build -t contact-form-server -f dockerfile .
```

Run the container and publish the port to the host (map host:container):

```powershell
# foreground, remove on exit
docker run --rm -p 4000:4000 -e WEBHOOK_URL="https://your-webhook" contact-form-server

# detached
docker run -d --name contact-form -p 4000:4000 -e WEBHOOK_URL="https://your-webhook" contact-form-server

# use an env file
docker run -d --name contact-form -p 4000:4000 --env-file .env contact-form-server
```

Verify the container is listening:

```powershell
docker ps
# look for PORTS column: 0.0.0.0:4000->4000/tcp
```

## Test the API
Example request (PowerShell):

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:4000/api/contact -ContentType 'application/json' -Body '{"name":"Test","email":"test@example.com","message":"hi"}'
```

If the request succeeds you should get a small JSON confirmation and the server will POST a formatted message to the configured `WEBHOOK_URL`.

## Troubleshooting
- If you cannot connect, ensure you published the port with `-p hostPort:containerPort` (e.g. `-p 4000:4000`).
- Check container logs: `docker logs <container-name>`.
- Confirm `WEBHOOK_URL` is set in the container environment (or `.env` is present when using `--env-file`).
- If running locally and webhook delivery fails, check the server stdout for errors — `main.py` prints delivery failures.

