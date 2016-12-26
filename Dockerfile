FROM python:3.5

RUN \
	apt-get update -y \
	&& apt-get install -y postgresql-client-9.4 vim

ENV TWOBRADLEYS_APP bigleague
ENV GIT_REPO twobradleys/bigleague

RUN mkdir -p /opt/bigleague
WORKDIR /opt/bigleague

COPY src/requirements.txt /tmp/requirements.txt

RUN \
	pip install --no-cache-dir -r /tmp/requirements.txt \
	&& rm /tmp/requirements.txt

COPY src /opt/bigleague

RUN \
	cd /opt/bigleague \
	&& pip install -e .

COPY .bashrc /root

EXPOSE 80

CMD ["bigleague-serve"]
