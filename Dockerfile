# django APP
# do not operate database in APP's docker
# for there would be several apps, sharing one database
#
FROM daocloud.io/python:2.7
MAINTAINER JackonYang <i@jackon.me>>

RUN apt-get update

# install packages from source code
RUN apt-get install -y wget
RUN apt-get install -y cmake


# http://stackoverflow.com/questions/23524976/capturing-output-of-python-script-run-inside-a-docker-container
ENV PYTHONUNBUFFERED=0


# https://docs.docker.com/engine/reference/builder/#arg
ARG pip_host=pypi.douban.com
ARG pip_root_url=http://pypi.douban.com/simple/

# upgrade pip to latest version
RUN pip install --upgrade pip -i $pip_root_url --trusted-host $pip_host

# logging
RUN pip install -i $pip_root_url --trusted-host $pip_host rollbar==0.13.8


# pygit2 and its dependencies
RUN wget https://github.com/libgit2/libgit2/archive/v0.24.0.tar.gz && \
tar xzf v0.24.0.tar.gz && \
cd libgit2-0.24.0/ && \
cmake . && \
make && \
make install
RUN ldconfig
RUN pip install -i $pip_root_url --trusted-host $pip_host pygit2==0.24.2


# common
RUN pip install -i $pip_root_url --trusted-host $pip_host redis==2.10.5

RUN pip install -i $pip_root_url --trusted-host $pip_host wechat_sdk


COPY . /src
WORKDIR /src

RUN pip install -r requirements.txt
