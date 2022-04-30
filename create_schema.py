from app import Application

Application.init_db_backend()
Application.database.create_schema()
