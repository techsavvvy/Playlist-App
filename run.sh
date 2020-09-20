pip3 install -r requirements.txt 

python3 create_db.py

python3 manage.py db init

python3 manage.py db migrate

python3 manage.py db upgrade

python3 manage.py runserver --port 8000
