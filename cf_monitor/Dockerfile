 
FROM python:3.7.2

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .

RUN apt-get update -q 
 
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# https://unix.stackexchange.com/questions/263801/apt-get-fails-the-method-driver-usr-lib-apt-methods-https-could-not-be-found
RUN apt-get install apt-transport-https ca-certificates

RUN apt-get update

# optional: for bcp and sqlcmd
RUN ACCEPT_EULA=Y apt-get -q -y install mssql-tools unixodbc-dev
RUN ACCEPT_EULA=Y apt-get -q -y install msodbcsql17
RUN ACCEPT_EULA=Y apt-get -q -y install msodbcsql18
RUN ACCEPT_EULA=Y apt-get -q -y install mssql-tools18
RUN apt update

RUN pip install --no-cache-dir -r  requirements.txt 

COPY main.py .  
COPY dbops.py .  
COPY config.py . 

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
