FROM python:3.4-slim

RUN groupadd -g 999 docker-user &&  useradd -r -u 999 -g docker-user docker-user
USER docker-user