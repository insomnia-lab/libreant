FROM archlinux/base

RUN pacman -Sqy --noconfirm \
	python2-setuptools \
	# setuptools unspecified dependencies: https://bugs.archlinux.org/task/56493?project=0&order=id&sort=desc&string=python2-virtualenv
	python2-virtualenv \
	grep \
	procps \
	elasticsearch

### BEFORE LIBREANT 0.6 ###

ENV LIBREANT_INST_DIR /libreant
  
# Import libreant source from current local folder
ADD . ${LIBREANT_INST_DIR}/
  
# Install libreant
WORKDIR $LIBREANT_INST_DIR
RUN virtualenv2 -p /usr/bin/python2 ve
RUN ./ve/bin/pip -q install .

EXPOSE 5000

CMD runuser -u elasticsearch -- /usr/sbin/elasticsearch -d; ./ve/bin/libreant
