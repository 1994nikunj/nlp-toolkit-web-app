# repo location $ FROM

LABEL Description="This image is used to start the Flask Web-App"
LABEL MAINTAINER="Nikunj Sharma"

ADD . /opt/app-root/src

RUN chmod -R 777 /opt/app-root/src

WORKDIR /opt/app-root/src

RUN pip install -r requirements.txt

EXPOSE 9002

CMD flask run --host 0.0.0.0
