# Steps to run


## With docker
1) Create the env file  RUN `mv env .env`
2) Fill in the google reCaptcha public and private key
3) RUN `docker-compose build` 
4) RUN `docker-compose up`
5) go to http://0.0.0.0:5000/register

## Without docker

Note:- Ensure that Python3 installed

1) Create the env file  RUN `mv env .env`
2) Fill in the google reCaptcha public and private key
3) RUN `pip3 install -r requirements.txt` 
4) RUN `pythton3 app.py`
5) go to http://0.0.0.0:5000/register