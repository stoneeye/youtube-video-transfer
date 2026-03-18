import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database import Video, Base

def clean_database():
    db_path = "data/history.db"
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return

    print(f"WARNING: This will delete ALL records in {db_path}!")
    print("Are you sure you want to proceed? (y/n)")
    choice = input().lower()
    
    if choice == 'y':
        try:
            # Connect to DB
            engine = create_engine(f'sqlite:///{db_path}')
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Delete all records
            deleted_count = session.query(Video).delete()
            session.commit()
            session.close()
            
            print(f"Successfully deleted {deleted_count} records.")
        except Exception as e:
            print(f"Error cleaning database: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    clean_database()
