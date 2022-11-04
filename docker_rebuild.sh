echo START
cd docker
docker-compose down
cd ..
docker rmi db-api
docker build . -t ssr-api -f docker/Dockerfile #--no-cache
cd docker
./docker_compose.sh
cd ..
echo END
docker logs -f docker_db-api_1
