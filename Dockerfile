FROM node:12.13-alpine
WORKDIR /app
COPY --chown=node:node webapp/*.json ./
RUN npm install
COPY --chown=node:node webapp/ ./
RUN npm run build

FROM python:3.8-alpine
WORKDIR /app
RUN pip install pipenv
COPY conductor/Pipfile* ./
RUN pipenv lock --requirements > requirements.txt
RUN pip install -r requirements.txt
COPY conductor/ ./
COPY --from=0 /app/build ./web/

ENV PORT=80 \
    LOG_LEVEL=INFO \
    CHALLENGE_TIMEOUT_SECONDS=5 \
    MAX_SOCKETS=10 \
    SECONDS_BEFORE_NEW_SESSION=3 \
    STATIC_FILES_PATH=web \
    TRIVIA_MAX_FETCH_TENTATIVES=3 \
    TRIVIA_FETCH_SIZE=25 \
    PYTHONPATH=/app

EXPOSE ${PORT}

CMD ["python", "conductor/server.py"]