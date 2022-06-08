FROM archlinux:latest

ENV PIP_NO_CACHE_DIR 1
WORKDIR /usr/src/app
RUN patched_glibc=glibc-linux4-2.33-4-x86_64.pkg.tar.zst && \
    curl -LO "https://repo.archlinuxcn.org/x86_64/$patched_glibc" && \
    bsdtar -C / -xvf "$patched_glibc"
RUN pacman -Syu --noconfirm \
    aria2 \
    python-lxml \
    curl \
    pv \
    jq \
    ffmpeg \
    python \
    fakeroot \
    p7zip \
    python-pip \
    openssl \
    wget \
    gcc \
    neofetch \
    ca-certificates \
    && rm -rf /var/cache/pacman/pkg /tmp

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY . .
COPY netrc /root/.netrc
COPY extract /usr/local/bin/extract
COPY supervisord.conf /etc/supervisord.conf
RUN chmod +x /usr/local/bin/extract && \
    chmod +x start.sh

CMD ["/bin/bash","start.sh"]
