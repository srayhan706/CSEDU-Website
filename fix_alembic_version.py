#!/usr/bin/env python3
"""
Script to fix the alembic_version table by updating the version_num
from the obsolete revision to the new merge revision.
"""
import psycopg2
from config import settings

# Database connection parameters from settings
params = {
    'host': 'localhost',
    'port': settings.database_port,
    'database': settings.database_name,
    'user': settings.database_username,
    'password': settings.database_password
}

# Connect to the database
print(f"Connecting to database {settings.database_name}...")
conn = psycopg2.connect(**params)
conn.autocommit = True
cursor = conn.cursor()

# Check current version
print("Checking current alembic_version...")
cursor.execute("SELECT version_num FROM alembic_version;")
current_versions = cursor.fetchall()
print(f"Current version(s): {current_versions}")

# Update to the new version
new_version = '7c3d2a4b5e6f_merge_final'
print(f"Updating alembic_version to {new_version}...")

# Delete all existing versions and insert the new one
cursor.execute("DELETE FROM alembic_version;")
cursor.execute("INSERT INTO alembic_version (version_num) VALUES (%s);", (new_version,))

# Verify the update
cursor.execute("SELECT version_num FROM alembic_version;")
updated_versions = cursor.fetchall()
print(f"Updated version(s): {updated_versions}")

# Close the connection
cursor.close()
conn.close()
print("Database connection closed.")
print("Done! You can now run 'alembic upgrade head'")
