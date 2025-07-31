install:
	uv

fmt:
	ruff format .
	ruff check . --fix

lint:
	ruff check .
	uv run mypy ./

test:
	uv run pytest --dead-fixtures
	uv run pytest -x --cov=./src/uploadanywhere --cov-branch --no-cov-on-fail --cov-report=xml --cov-report=html --junit-xml=coverage.xml

new_migration:
	migrate create -ext .sql -dir ./src/uploadanywhere/infrastructure/postgres/migrations $$NAME

migrate:
	migrate -database "postgres://guest:guest@localhost:5432/guest?sslmode=disable" -path ./src/uploadanywhere/infrastructure/postgres/migrations up

unmigrate:
	migrate -database "postgres://guest:guest@localhost:5432/guest?sslmode=disable" -path ./src/uploadanywhere/infrastructure/postgres/migrations down