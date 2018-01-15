FROM debian:stable
# we cannot use the slimmified version of debian stable because of this bug https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=863199

RUN apt-get -q update && apt-get install -qy --no-install-recommends \
		apt-transport-https \
		curl \
		gnupg \
		ca-certificates

# Install elasticsearch
RUN curl --silent --show-error "https://artifacts.elastic.co/GPG-KEY-elasticsearch" | apt-key add -

RUN echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" > /etc/apt/sources.list.d/elastic-6.x.list

RUN apt-get -q update && apt-get install -qy --no-install-recommends \
		openjdk-8-jre-headless \
		procps \
		# the ps command is required by elasticsearch startup script
		elasticsearch

# Install the base system requirements: python, pip
RUN apt-get -q update && apt-get install -qy --no-install-recommends \
		python2.7 \
		python-wheel \
		virtualenv \
&& rm -rf /var/lib/apt/lists/*

ENV LIBREANT_INST_DIR /libreant
  
# Import libreant source from current local folder
ADD . ${LIBREANT_INST_DIR}/
  
# Install libreant
WORKDIR $LIBREANT_INST_DIR
RUN virtualenv -p /usr/bin/python2.7 ve
RUN ./ve/bin/pip -q install .

EXPOSE 5000

# we bypass systemd to run elasticsearch
CMD bash /libreant/.docker/inside-runlibreant
