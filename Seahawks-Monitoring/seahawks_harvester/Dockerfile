FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y \
    nmap \
    iputils-ping \
    git \
 && apt-get clean

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x update.sh

EXPOSE 5000

CMD ["bash", "-c", "./update_harvester.sh && python app.py"]
