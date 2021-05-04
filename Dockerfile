FROM labjack/ljm
# https://hub.docker.com/r/labjack/ljm

WORKDIR /usr/src/app

#COPY requirements.txt ./
#RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "./labjackVisual.py" ]
