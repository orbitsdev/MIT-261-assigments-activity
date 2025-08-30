class Config:
    # Using your provided Atlas URI + DB name for immediate use
    MONGO_URI = (
        "mongodb+srv://orbitsdev:%40Password@cluster0.q8v3kcn.mongodb.net/"
        "mit261?retryWrites=true&w=majority&appName=Cluster0"
    )
    MONGO_DB_NAME = "mit261"
    SECRET_KEY = "dev-only-secret"
