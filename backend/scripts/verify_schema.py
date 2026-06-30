import sqlite3

conn = sqlite3.connect("predictiveops.db")
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print("Tables:", [t[0] for t in tables])

indexes = [i[0] for i in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name"
).fetchall()]
print("Custom indexes:", indexes)

cols = [c[1] for c in conn.execute("PRAGMA table_info(incidents)").fetchall()]
print("Incident columns:", cols)

user_cols = [c[1] for c in conn.execute("PRAGMA table_info(users)").fetchall()]
print("User columns:", user_cols)

alert_cols = [c[1] for c in conn.execute("PRAGMA table_info(alerts)").fetchall()]
print("Alert columns:", alert_cols)

alembic_ver = conn.execute("SELECT version_num FROM alembic_version").fetchall()
print("Alembic version:", alembic_ver)

conn.close()
