"""
db_repair_tool.py
Safe SQLite diagnostic and basic recovery helper for hospital.db.

Usage: run from the folder containing hospital.db:
    python db_repair_tool.py

It will create diagnostic files:
  - db_diagnostic.txt        (summary & outputs)
  - hospital_dump.sql       (SQL dump if export succeeds)
  - hospital_table_<name>.csv  (CSV exports of each table)

It will NOT overwrite hospital.db. If it needs to create a fresh DB it will ask you first.
"""

import sqlite3, os, shutil, datetime, csv, traceback

DB = "hospital.db"
DIAG = "db_diagnostic.txt"

def writeline(f, s=""):
    f.write(s + "\n")
    print(s)

def run():
    with open(DIAG, "w", encoding="utf-8") as out:
        writeline(out, f"DB diagnostic run at {datetime.datetime.now().isoformat()}")
        if not os.path.exists(DB):
            writeline(out, f"ERROR: Database file '{DB}' not found in current folder: {os.getcwd()}")
            writeline(out, "If your DB is somewhere else, move it here or run this tool from the correct folder.")
            return

        # Make backup copy first
        backup_name = f"{DB}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2(DB, backup_name)
            writeline(out, f"Backup created: {backup_name}")
        except Exception as e:
            writeline(out, f"Warning: could not create backup copy: {e}")
            writeline(out, "You should manually copy the file before proceeding.")

        # Try opening the DB
        try:
            conn = sqlite3.connect(DB, timeout=10)
            cur = conn.cursor()
            writeline(out, "Opened DB successfully.")
        except Exception as e:
            writeline(out, "ERROR: Failed to open DB:")
            writeline(out, str(e))
            writeline(out, traceback.format_exc())
            return

        # 1) PRAGMA integrity_check
        try:
            cur.execute("PRAGMA integrity_check;")
            rows = cur.fetchall()
            writeline(out, "")
            writeline(out, "PRAGMA integrity_check result:")
            for r in rows:
                writeline(out, repr(r))
        except Exception as e:
            writeline(out, "")
            writeline(out, "ERROR running integrity_check:")
            writeline(out, str(e))
            writeline(out, traceback.format_exc())

        # 2) Show schema
        try:
            writeline(out, "")
            writeline(out, "Schema (sqlite_master):")
            cur.execute("SELECT type, name, tbl_name, sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type, name;")
            for t, name, tbl, sql in cur.fetchall():
                writeline(out, f"-- {t} {name} ({tbl})")
                writeline(out, sql)
                writeline(out, "")
        except Exception as e:
            writeline(out, "ERROR reading schema:")
            writeline(out, str(e))

        # 3) List tables
        try:
            writeline(out, "")
            writeline(out, "Tables and row counts:")
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [r[0] for r in cur.fetchall()]
            if not tables:
                writeline(out, "No user tables found.")
            for table in tables:
                try:
                    cur.execute(f"SELECT count(*) FROM \"{table}\";")
                    cnt = cur.fetchone()[0]
                    writeline(out, f" - {table}: {cnt} rows")
                except Exception as e:
                    writeline(out, f" - {table}: ERROR counting rows: {e}")
        except Exception as e:
            writeline(out, "ERROR listing tables:")
            writeline(out, str(e))

        # 4) Dump each table to CSV (best-effort)
        writeline(out, "")
        writeline(out, "Attempting CSV export of each table (best-effort).")
        for table in tables:
            try:
                cur.execute(f"PRAGMA table_info('{table}');")
                cols = [c[1] for c in cur.fetchall()]
                cur.execute(f"SELECT * FROM \"{table}\" LIMIT 10000;")
                rows = cur.fetchall()
                csv_name = f"hospital_table_{table}.csv"
                with open(csv_name, "w", newline='', encoding="utf-8") as csvf:
                    writer = csv.writer(csvf)
                    writer.writerow(cols)
                    writer.writerows(rows)
                writeline(out, f"  exported {table} -> {csv_name} ({len(rows)} rows exported)")
            except Exception as e:
                writeline(out, f"  FAILED exporting {table}: {e}")

        # 5) Try to generate SQL dump
        try:
            writeline(out, "")
            writeline(out, "Attempting SQL dump (sqlite .dump style) to hospital_dump.sql")
            dump_file = "hospital_dump.sql"
            with open(dump_file, "w", encoding="utf-8") as df:
                for line in conn.iterdump():
                    df.write(f"{line}\n")
            writeline(out, f"SQL dump written to {dump_file}")
        except Exception as e:
            writeline(out, f"SQL dump failed: {e}")

        # 6) Try VACUUM (only if integrity_check returned 'ok')
        try:
            cur.execute("PRAGMA integrity_check;")
            res = cur.fetchone()
            ok = False
            if res and (('ok' in res[0].lower()) or res[0] == 'ok'):
                ok = True
            if ok:
                writeline(out, "")
                writeline(out, "Integrity is OK. Attempting VACUUM to rebuild the database file (may shrink file).")
                try:
                    cur.execute("VACUUM;")
                    conn.commit()
                    writeline(out, "VACUUM completed.")
                except Exception as e:
                    writeline(out, f"VACUUM failed: {e}")
            else:
                writeline(out, "")
                writeline(out, "Integrity check did NOT return OK. Skipping VACUUM to avoid worsening corruption.")
        except Exception as e:
            writeline(out, f"Error during vacuum/extra checks: {e}")

        # Close
        cur.close()
        conn.close()
        writeline(out, "")
        writeline(out, "Diagnostic finished. Look at the generated files for details:")
        writeline(out, f" - {DIAG}")
        writeline(out, " - hospital_dump.sql (if created)")
        writeline(out, " - hospital_table_<name>.csv (per-table CSVs)")
        writeline(out, "")
        writeline(out, "If integrity_check reported corruption or dump failed, reply here and paste the last part of db_diagnostic.txt. I'll help recover or rebuild the DB.")
        writeline(out, "If CSVs were produced, you can use them to rebuild a fresh DB (I can provide that script).")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("Diagnostic tool crashed:", e)
        import traceback
        traceback.print_exc()
