https://github.com/sdplatt/pyweb/wiki/FastAPI


python -m venv .env
source .env/bin/activate

pip install fastapi
pip install "uvicorn[standard]" OR pip install hypercorn

?python3.10 -m venv .venv #.venv hidden


## Access via main.py


# RUNNING It with a specific poet

uvicorn main:app --reload --port 8001

## TESTING IT

Insommia

GET http://127.0.0.1:8001 

Browser
http://127.0.0.1:8001/docs


pip install -r requirements.txt
pip freeze > requirements.txt OK

## routes
storeTMX
use 
UUID('120ce9a9-0d79-4b28-a4fe-7c604a99ba5f') as clientId
120ce9a9-0d79-4b28-a4fe-7c604a99ba5f
http://127.0.0.1:8001/storeTMX/?clientId=120ce9a9-0d79-4b28-a4fe-7c604a99ba5f