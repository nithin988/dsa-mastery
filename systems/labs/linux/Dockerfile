# Optional practice environment for Systems Mastery labs: a disposable Debian with the usual tools.
#   docker build -t sys-lab https://github.com/nithin988/dsa-mastery.git#main:systems/labs/linux
#   docker run --rm -it sys-lab lab workshop
FROM debian:trixie-slim
RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
      procps psmisc less file tree git curl strace lsof dnsutils iproute2 bc vim-tiny sysstat tcpdump iputils-ping ca-certificates man-db \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash learner
COPY *.sh /labs/
COPY lab /usr/local/bin/lab
RUN chmod +x /usr/local/bin/lab /labs/*.sh
USER learner
WORKDIR /home/learner
CMD ["bash"]
