FROM revolutionsystems/python:3.8.9-wee-optimized-lto as base

ENV PYTHONBREAKPOINT=ipdb.set_trace \
    DEBIAN_FRONTEND=noninteractive \
    PG_MAJOR=13

RUN set -ex; \
	if ! command -v gpg > /dev/null; then \
		apt-get update; \
		apt-get install -y --no-install-recommends \
			gnupg \
			dirmngr \
		; \
		rm -rf /var/lib/apt/lists/*; \
	fi

RUN set -ex; \
# pub   4096R/ACCC4CF8 2011-10-13 [expires: 2019-07-02]
#       Key fingerprint = B97B 0AFC AA1A 47F0 44F2  44A0 7FCC 7D46 ACCC 4CF8
# uid                  PostgreSQL Debian Repository
	key='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8'; \
	export GNUPGHOME="$(mktemp -d)"; \
	gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$key"; \
	gpg --batch --export "$key" > /etc/apt/trusted.gpg.d/postgres.gpg; \
	command -v gpgconf > /dev/null && gpgconf --kill all; \
	rm -rf "$GNUPGHOME"; \
	apt-key list

RUN set -xe; \
  	echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main $PG_MAJOR" > /etc/apt/sources.list.d/pgdg.list; \
  	apt-get update; \
  	apt-get install -y --no-install-recommends \
    curl \
    make \
    apt-transport-https \
	ca-certificates \
	lzma \
	gettext \
	libc6-dev \
	gcc \
	libevent-dev \
	libffi-dev \
	libpng-dev \
    libjpeg-dev \
	zlib1g-dev \
	libtiff-dev \
	libfreetype6 \
	libwebp-dev \
	libpq-dev \
	postgresql-client-$PG_MAJOR; \
    find /var/lib/apt/lists \
		/usr/share/man \
		/usr/share/doc \
		/var/log \
		-type f -exec rm -f {} +

RUN mkdir -p /app
WORKDIR /app

###############################################################################
FROM base as boot

RUN mkdir -p /init && mkdir -p /init/boot
COPY compose/build/opt/supervisord.conf /init/supervisord.conf
RUN set -xe; \
  pip install "supervisor>=4,<5"; \
  ln -s /init/supervisord.conf  /usr/local/supervisord.conf

ENTRYPOINT ["supervisord", "-c", "/init/supervisord.conf", "--"]

###############################################################################
FROM boot as deps

COPY src/requirements /requirements
RUN pip install --pre -r /requirements/runtime.txt && rm -rf /requirements; \
    find /usr/lib/python3/dist-packages/ \
		-type d -name __pycache__ -empty -print0 | xargs --null --no-run-if-empty rmdir

###############################################################################
FROM deps as ci

RUN set -xe; \
  	apt-get update; \
  	apt-get install -y --no-install-recommends \
	  shellcheck; \
    find /var/lib/apt/lists \
		/usr/share/man \
		/usr/share/doc \
		/var/log \
		-type f -exec rm -f {} +

COPY src/requirements /requirements
RUN pip install --pre -r /requirements/local.txt && rm -rf /requirements; \
	find /usr/lib/python3/dist-packages/ \
		-type d -name __pycache__ -empty -print0 | xargs --null --no-run-if-empty rmdir

###############################################################################
FROM deps as cd

ADD src /app
COPY src/boot/boot.conf /init/boot/boot.conf
RUN chmod -R +x /app/boot

###############################################################################
FROM deps as local

COPY src/requirements /requirements
RUN pip install -r /requirements/local.txt && rm -rf /requirements
