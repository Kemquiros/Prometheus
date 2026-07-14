FROM python:3.12-slim AS builder

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir build \
    && python -m build --wheel --outdir /app/dist

FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /app/dist/*.whl /tmp/

RUN pip install --no-cache-dir /tmp/*.whl \
    && rm -rf /tmp/*.whl

ENTRYPOINT ["prometheus"]
CMD ["--help"]
