# FastAPI Project - Development

## Docker Compose

* Start the local stack with Docker Compose:

```bash
docker compose watch
```

* Now you can open your browser and interact with these URLs:

Frontend, built with Docker, with routes handled based on the path: http://localhost:5173

Backend, JSON based web API based on OpenAPI: http://localhost:8000

Automatic interactive documentation with Swagger UI (from the OpenAPI backend): http://localhost:8000/docs

Adminer, database web administration: http://localhost:8080

Traefik UI, to see how the routes are being handled by the proxy: http://localhost:8090

**Note**: The first time you start your stack, it might take a minute for it to be ready. While the backend waits for the database to be ready and configures everything. You can check the logs to monitor it.

To check the logs, run (in another terminal):

```bash
docker compose logs
```

To check the logs of a specific service, add the name of the service, e.g.:

```bash
docker compose logs backend
```

## Local Development

The Docker Compose files are configured so that each of the services is available in a different port in `localhost`.

For the backend and frontend, they use the same port that would be used by their local development server, so, the backend is at `http://localhost:8000` and the frontend at `http://localhost:5173`.

This way, you could turn off a Docker Compose service and start its local development service, and everything would keep working, because it all uses the same ports.

For example, you can stop that `frontend` service in the Docker Compose, in another terminal, run:

```bash
docker compose stop frontend
```

And then start the local frontend development server:

```bash
cd frontend
npm run dev
```

Or you could stop the `backend` Docker Compose service:

```bash
docker compose stop backend
```

And then you can run the local development server for the backend:

```bash
cd backend
fastapi dev app/main.py
```

## Docker Compose in `localhost.tiangolo.com`

When you start the Docker Compose stack, it uses `localhost` by default, with different ports for each service (backend, frontend, adminer, etc).

When you deploy it to production (or staging), it will deploy each service in a different subdomain, like `api.example.com` for the backend and `dashboard.example.com` for the frontend.

In the guide about [deployment](deployment.md) you can read about Traefik, the configured proxy. That's the component in charge of transmitting traffic to each service based on the subdomain.

If you want to test that it's all working locally, you can edit the local `.env` file, and change:

```dotenv
DOMAIN=localhost.tiangolo.com
```

That will be used by the Docker Compose files to configure the base domain for the services.

Traefik will use this to transmit traffic at `api.localhost.tiangolo.com` to the backend, and traffic at `dashboard.localhost.tiangolo.com` to the frontend.

The domain `localhost.tiangolo.com` is a special domain that is configured (with all its subdomains) to point to `127.0.0.1`. This way you can use that for your local development.

After you update it, run again:

```bash
docker compose watch
```

When deploying, for example in production, the main Traefik is configured outside of the Docker Compose files. For local development, there's an included Traefik in `docker-compose.override.yml`, just to let you test that the domains work as expected, for example with `api.localhost.tiangolo.com` and `dashboard.localhost.tiangolo.com`.

## Docker Compose files and env vars

There is a main `docker-compose.yml` file with all the configurations that apply to the whole stack, it is used automatically by `docker compose`.

And there's also a `docker-compose.override.yml` with overrides for development, for example to mount the source code as a volume. It is used automatically by `docker compose` to apply overrides on top of `docker-compose.yml`.

These Docker Compose files use the `.env` file containing configurations to be injected as environment variables in the containers.

They also use some additional configurations taken from environment variables set in the scripts before calling the `docker compose` command.

After changing variables, make sure you restart the stack:

```bash
docker compose watch
```

## The .env file

The `.env` file is the one that contains all your configurations, generated keys and passwords, etc.

Depending on your workflow, you could want to exclude it from Git, for example if your project is public. In that case, you would have to make sure to set up a way for your CI tools to obtain it while building or deploying your project.

One way to do it could be to add each environment variable to your CI/CD system, and updating the `docker-compose.yml` file to read that specific env var instead of reading the `.env` file.

## Telegram Bot Development

This project includes a Telegram bot that can be tested and developed locally.

### Setup Telegram Bot for Development

1. **Get a Bot Token**:
   - Go to [@BotFather](https://t.me/BotFather) on Telegram
   - Create a new bot with `/newbot` (or use an existing one)
   - Copy the token

2. **Configure `.env` file**:
   Add these variables to your `.env` file:

   ```dotenv
   TELEGRAM_ENABLED=true
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_WEBHOOK_SECRET=your_random_secret_here
   RUN_BOT_POLLING=true
   SERVER_HOST=http://localhost:8000
   ```

   For development, use `RUN_BOT_POLLING=true` (polling mode) which is simpler than webhook mode.

3. **Generate Webhook Secret** (optional, but recommended):
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(16))"
   ```

### Testing the Bot Locally

1. **Start the stack**:
   ```bash
   docker compose watch
   ```

2. **Check bot logs**:
   ```bash
   docker compose logs backend | grep -i telegram
   ```

   You should see:
   ```
   INFO Telegram bot started in polling mode
   ```

3. **Test the bot**:
   - Open Telegram and find your bot
   - Send `/start` command
   - The bot should respond with a welcome message

### Testing Deep Link Authentication

The bot supports deep link authentication. To test it:

1. **Get a start token** (as superuser):
   ```bash
   # First, get an access token by logging in via API
   curl -X POST "http://localhost:8000/api/v1/login/access-token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@example.com&password=your_password"
   ```

2. **Generate a debug token**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/debug-token?user_id=<user_uuid>" \
     -H "Authorization: Bearer <access_token>"
   ```

3. **Test the deep link**:
   - In Telegram, send: `/start <token>`
   - Or use the link: `https://t.me/your_bot_username?start=<token>`

### Disable Bot for Development

If you don't want to use the bot during development, set in `.env`:

```dotenv
TELEGRAM_ENABLED=false
```

The application will start without the bot, and you won't see Telegram-related errors in logs.

### Local Development Without Docker

If you're running the backend locally (not in Docker):

```bash
cd backend
fastapi dev app/main.py
```

Make sure your `.env` file has the Telegram configuration. The bot will work the same way, using polling mode by default.

### Debugging Bot Issues

* **Bot doesn't respond**: Check `TELEGRAM_BOT_TOKEN` is correct and `TELEGRAM_ENABLED=true`
* **Network errors**: The Docker container has DNS configured (8.8.8.8, 8.8.4.4) to resolve `api.telegram.org`
* **Token errors**: Verify the token format is correct (should be like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
* **Check logs**: Always check `docker compose logs backend` for detailed error messages

## Pre-commits and code linting

we are using a tool called [pre-commit](https://pre-commit.com/) for code linting and formatting.

When you install it, it runs right before making a commit in git. This way it ensures that the code is consistent and formatted even before it is committed.

You can find a file `.pre-commit-config.yaml` with configurations at the root of the project.

#### Install pre-commit to run automatically

`pre-commit` is already part of the dependencies of the project, but you could also install it globally if you prefer to, following [the official pre-commit docs](https://pre-commit.com/).

After having the `pre-commit` tool installed and available, you need to "install" it in the local repository, so that it runs automatically before each commit.

Using `uv`, you could do it with:

```bash
❯ uv run pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

Now whenever you try to commit, e.g. with:

```bash
git commit
```

...pre-commit will run and check and format the code you are about to commit, and will ask you to add that code (stage it) with git again before committing.

Then you can `git add` the modified/fixed files again and now you can commit.

#### Running pre-commit hooks manually

you can also run `pre-commit` manually on all the files, you can do it using `uv` with:

```bash
❯ uv run pre-commit run --all-files
check for added large files..............................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
eslint...................................................................Passed
prettier.................................................................Passed
```

## URLs

The production or staging URLs would use these same paths, but with your own domain.

### Development URLs

Development URLs, for local development.

Frontend: http://localhost:5173

Backend: http://localhost:8000

Automatic Interactive Docs (Swagger UI): http://localhost:8000/docs

Automatic Alternative Docs (ReDoc): http://localhost:8000/redoc

Adminer: http://localhost:8080

Traefik UI: http://localhost:8090

MailCatcher: http://localhost:1080

**Telegram Bot**: Available in Telegram after starting the stack (if `TELEGRAM_ENABLED=true`)

### Development URLs with `localhost.tiangolo.com` Configured

Development URLs, for local development.

Frontend: http://dashboard.localhost.tiangolo.com

Backend: http://api.localhost.tiangolo.com

Automatic Interactive Docs (Swagger UI): http://api.localhost.tiangolo.com/docs

Automatic Alternative Docs (ReDoc): http://api.localhost.tiangolo.com/redoc

Adminer: http://localhost.tiangolo.com:8080

Traefik UI: http://localhost.tiangolo.com:8090

MailCatcher: http://localhost.tiangolo.com:1080

**Telegram Bot**: Available in Telegram after starting the stack (if `TELEGRAM_ENABLED=true`)

**Debug Token Endpoint**: http://api.localhost.tiangolo.com/api/v1/debug-token (requires authentication)