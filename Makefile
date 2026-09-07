dev:
	bun run --filter frontend dev & \
	uv run uvicorn app.main:app --reload & \
	wait