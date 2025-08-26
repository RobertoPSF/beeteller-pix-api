.PHONY:

build:
	docker compose down -v
	-docker network rm beeteller-pix-api_default 2>/dev/null || true
	docker compose up --build
