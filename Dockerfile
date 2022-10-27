FROM python:3.10-slim-buster AS builder
ENV PATH=/usr/local/bin:$PATH

WORKDIR .
COPY . .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*
RUN cp index.html /usr/local/lib/python3.10/site-packages/streamlit/static/index.html && \
    cp favicon.png /usr/local/lib/python3.10/site-packages/streamlit/static/favicon.png && \
    find /usr/local/lib/python3.10/site-packages/streamlit -type f \( -iname \*.py -o -iname \*.js \) -print0 | xargs -0 sed -i 's/healthz/health-check/g'

# We are doing a 2-stage build to make it lighter
FROM python:3.10-slim-buster AS app
COPY --from=builder /usr/local /usr/local
COPY --from=builder . .
ENV PATH=/usr/local/bin:$PATH

# streamlit-specific commands for config
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

EXPOSE 8080

WORKDIR .

ENTRYPOINT [ "streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false"]




