docker pull postgres

docker run --name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v "%cd%/volume:/var/lib/postgresql" postgres