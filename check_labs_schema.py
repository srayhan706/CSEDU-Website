from sqlalchemy import create_engine, inspect
from database import engine

def check_labs_schema():
    # Use the existing engine
    # engine is already defined in database.py
    
    # Create inspector
    inspector = inspect(engine)
    
    # Get table names
    table_names = inspector.get_table_names()
    print(f"Available tables: {table_names}")
    
    # Check if labs table exists
    if "labs" in table_names:
        print("\nLabs table exists. Checking columns...")
        
        # Get columns for labs table
        columns = inspector.get_columns("labs")
        print("\nColumns in labs table:")
        for column in columns:
            print(f"- {column['name']} (Type: {column['type']})")
    else:
        print("\nLabs table does not exist in the database.")
    
    # Check if lab_time_slots table exists
    if "lab_time_slots" in table_names:
        print("\nLab time slots table exists. Checking columns...")
        
        # Get columns for lab_time_slots table
        columns = inspector.get_columns("lab_time_slots")
        print("\nColumns in lab_time_slots table:")
        for column in columns:
            print(f"- {column['name']} (Type: {column['type']})")
    else:
        print("\nLab time slots table does not exist in the database.")

if __name__ == "__main__":
    check_labs_schema()
