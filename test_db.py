from database import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE()"))
        database_name = result.scalar()

        print("MySQL Database Connected Successfully!")
        print("Database Name:", database_name)

except Exception as e:
    print("Database Connection Failed!")
    print("Error:", e)