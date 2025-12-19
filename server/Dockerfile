FROM alpine:latest

# Install dependencies
RUN apk add --no-cache \
    openssh \
    openrc \
    python3 \
    py3-pip \
    bash \
    sudo \
    gocryptfs \
    fuse \
    rsync \
    openssl

# Configure SSH
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#StrictModes yes/StrictModes no/' /etc/ssh/sshd_config

# Create admin user
RUN adduser -D -s /bin/bash admin && \
    echo "admin ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/admin && \
    chmod 0440 /etc/sudoers.d/admin

# Install ENC tool (from server source)
WORKDIR /app
# Copy the entire server directory to /app
COPY server/ /app/
ENV BUILD_DATE=20241216_MIGRATION
RUN pip install . --break-system-packages

# Copy Restricted Shell (now in src)
# shell.py location is at /app/src/enc_server/shell.py
# But we copy it to bin for easy access as simple script
COPY server/src/enc_server/shell.py /usr/local/bin/enc-shell
COPY server/config/policy.json /etc/enc/policy.json
RUN chmod +x /usr/local/bin/enc-shell && chmod 644 /etc/enc/policy.json
ENV ENC_MODE=SERVER

# Setup Entrypoint
COPY server/scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

ENTRYPOINT ["/entrypoint.sh"]
