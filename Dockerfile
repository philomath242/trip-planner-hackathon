FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh


ENV PATH="/root/.local/bin/:$PATH"

COPY . .

RUN uv venv --clear && . .venv/bin/activate && uv pip install -r pyproject.toml

EXPOSE 5000

CMD [".venv/bin/python", "main.py"]