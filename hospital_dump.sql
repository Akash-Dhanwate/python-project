BEGIN TRANSACTION;
CREATE TABLE audit_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      operator_name TEXT,
      operator_role TEXT,
      action TEXT,
      ref_val TEXT,
      ts TEXT
    );
CREATE TABLE hospital (
      nameoftablets TEXT,
      Refrence TEXT,
      dose TEXT,
      nooftablets TEXT,
      issuedate TEXT,
      expdate TEXT,
      dailydose TEXT,
      sideeffect TEXT,
      nameofpatient TEXT,
      dob TEXT,
      patientaddress TEXT
    );
INSERT INTO "hospital" VALUES('wf','saf','sdwesadfd','df','dfdf','sasadfs','sasadfasd','f','as','dfsas','dffdfasdf');
INSERT INTO "hospital" VALUES('zfbdf','gfgfgfg','fdgadfggaf','','fgf','ggf','f','ggfgfg','','','g');
DELETE FROM "sqlite_sequence";
COMMIT;
