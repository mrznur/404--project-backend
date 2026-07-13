"""Reset annotation tables to match new Base64 model schema."""
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Drop old tables
cursor.execute('DROP TABLE IF EXISTS annotations_annotation')
cursor.execute('DROP TABLE IF EXISTS annotations_uploadedimage')

# Remove migration record so Django re-applies it
cursor.execute("DELETE FROM django_migrations WHERE app='annotations'")

conn.commit()
print('Done: dropped annotation tables and cleared migration record.')
conn.close()
