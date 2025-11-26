# syntax=docker/dockerfile:1

FROM alpine:3.19

LABEL org.opencontainers.image.title="docker-gammu-smsd"
LABEL org.opencontainers.image.description="Gammu SMS Daemon with Telegram notification support"
LABEL org.opencontainers.image.source="https://github.com/m0ntyG/docker-gammu-smsd"

# Install required packages
RUN apk add --no-cache \
        ca-certificates \
        dumb-init \
        gammu-smsd \
        libdbi-drivers \
        openssl \
        py3-requests \
        python3 \
    && mkdir -p /var/spool/sms/{inbox,outbox,sent,error}

# Copy configuration and scripts
COPY gammu-smsd /etc/gammu-smsd
COPY onreceive.py /etc/onreceive.py

# Make the receive script executable
RUN chmod +x /etc/onreceive.py

# Environment variables for Telegram integration
ENV CHAT_ID=""
ENV BOT_TOKEN=""
ENV PROXY=""

ENTRYPOINT ["/usr/bin/dumb-init", "--", "gammu-smsd", "-c", "/etc/gammu-smsd"]
