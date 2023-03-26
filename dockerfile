FROM selenium/standalone-chrome
LABEL Maintainer="abossuet"

WORKDIR /usr/app/src

USER root
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN python3 -m pip install selenium


COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . .

CMD ["python3", "./main.py"]