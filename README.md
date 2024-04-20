##  Auto Uopdate Code using SH Script 

### Initial Setup
```sh
    - Add Flask App
    - Create Deployment.sh
    - give rightes chmod +rwx filename.sh
    - Initial Setup of Gunicorn and Nginx
```

### SH Script

```sh
# Simple gunicorn Setup
#!/bin/bash
sudo apt-get update
git stash
git pull
python3 -m venv env
source env/bin/activate
pip install flask gunicorn
sudo pkill gunicorn  # kill alredy existing gunicorn 
gunicorn -w 5 -b 0.0.0.0:8080 --reload wsgi:app

```

```py 
project/
│
├── Backend/
│   ├── __init__.py
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       └── style.css
│
└── wsgi.py


# Backend/app.py

other logic ....
if __name__ == '__main__':
    app.run(debug=True)


# wsgi.py

from Backend.app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

# Gunicorn Run Code

gunicorn -w 5 -b 0.0.0.0:8080 --reload wsgi:app

```

