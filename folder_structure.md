MIT-261-assignments-activity/
│
├── .venv/                         # virtual environment
├── .env                           # environment variables (MONGO_USER, MONGO_PASS, MONGO_HOST)
├── app.py                         # tiny runner; delegates to app factory
├── config.py                      # config (Mongo URI, SECRET_KEY, etc.)
├── requirements.txt               # project dependencies
├── students_list.csv              # exported student data
├── subjects_list.csv             # exported subject data
├── runcommand.md                 # commands to run each script
│
├── app/                          # Flask application
│   ├── __init__.py               # app factory; registers blueprints
│   ├── extensions.py             # shared clients (pymongo)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── labs.py               # lab/assignment endpoints
│   │   └── session2_classlist.py  # Session 2 class list endpoints
│   ├── services/
│   │   └── classlist_service.py  # Service for class list operations
│   ├── templates/                # HTML views
│   │   └── session2/
│   │       └── classlist.html      # Class list template
│   └── static/                   # static assets
│
├── scripts/                      # Python scripts for each activity
│   ├── session1_student_subject_list.py      # Activity 1: Student and Subject Lists
│   ├── session1_LO-2MapReducePySpark.py      # Activity 2: MapReduce with MongoDB/Pandas
│   └── session1_LO-1ParallelvsDistributed.py # Activity 3: Parallel vs Distributed Computing
│
└── documentation/                # Markdown documentation for each activity
    ├── session_1_studentlist_and_subject_list.md
    ├── session_1_LO-2MapReducePySpark.md
    └── session_1_LO-1ParallelvsDistributed.md
