my_flask_project/
│
├── .venv/                         # your virtual environment
├── app.py                         # tiny runner; delegates to app factory
├── config.py                      # config (Mongo URI, SECRET_KEY, etc.)
├── requirements.txt
│
└── app/
    ├── __init__.py                # app factory; registers blueprints
    ├── extensions.py              # shared clients (pymongo)
    ├── routes/
    │   ├── __init__.py
    │   └── labs.py                # ALL lab/assignment endpoints live here
    ├── templates/
    │   └── base.html              # optional (for any HTML views)
    └── static/
        └── css/main.css           # optional
