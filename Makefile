start:
	poetry run flask --app backend:app run --host=0.0.0.0

build:
	./build.sh
