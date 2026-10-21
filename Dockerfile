FROM node:22.14.0-bookworm-slim AS codex
RUN npm install --prefix /opt/codex @openai/codex@0.163.0

FROM python:3.12.8-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends git ripgrep less ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=codex /usr/local/bin/node /usr/local/bin/node
COPY --from=codex /opt/codex /opt/codex
RUN ln -s /opt/codex/node_modules/.bin/codex /usr/local/bin/codex
COPY requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir -r /opt/requirements.txt \
    && useradd --create-home --uid 1000 eval \
    && mkdir /workspace && chown eval:eval /workspace
ENV HOME=/home/eval CODEX_HOME=/home/eval/.codex PYTHONPATH=/workspace/src \
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 TZ=UTC
WORKDIR /workspace
USER eval
CMD ["sleep", "infinity"]
