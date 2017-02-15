FROM python:2.7.13-wheezy
RUN apt-get update

RUN apt-get -y install wget gzip gcc make openssl libssl-dev rsync mysql-client vim libmysqlclient-dev

# install easy_install then pip
RUN pip2.7 install setuptools 
# pypi is not reliable to use for installation of s3_mysql_backup
WORKDIR /s3_mysql_backup
RUN git clone https://github.com/fogcitymarathoner/s3_mysql_backup.git
WORKDIR /s3_mysql_backup/s3_mysql_backup
RUN python2.7 setup.py install
COPY . /code
WORKDIR /code
RUN pip2.7 install Flask
RUN python2.7 setup.py install 
RUN ls /usr/local/bin
RUN mkdir -p /src/python-source
RUN mkdir /keyzcar
RUN mkdir /datadir
RUN mkdir /backups
RUN rm -rf /code /s3_mysql_backup
