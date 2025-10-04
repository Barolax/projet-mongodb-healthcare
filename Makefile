up:
	docker compose up -d mongo

migrate:
	docker compose build migrator
	docker compose up migrator

test:
	docker compose run --rm tester

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=100 mongo