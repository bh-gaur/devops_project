FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY operator/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runner

WORKDIR /workspace

RUN groupadd -g 10002 operatorgroup && \
    useradd -u 10002 -g operatorgroup -s /sbin/nologin -M operatoruser

COPY --from=builder /install /usr/local
COPY operator/ /workspace/operator/
COPY ansible/ /workspace/ansible/

RUN chown -R operatoruser:operatorgroup /workspace

USER 10002:10002

ENV PYTHONPATH=/workspace \
    PYTHONUNBUFFERED=1

CMD ["python", "operator/watcher.py"]
