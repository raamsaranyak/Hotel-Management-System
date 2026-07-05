import sqlite3 
b=sqlite3.connect("hotel.db") 
c=sqlite3.connect("instance/hotel.db") 
for t in [r[0] for r in b.execute("SELECT name FROM sqlite_master WHERE type='table'") if r[0] not in ("sqlite_sequence","alembic_version")]: 
  bc=[d[0] for d in b.execute(f"PRAGMA table_info({t})")] 
  br=b.execute(f"SELECT * FROM {t}").fetchall() 
  cr=c.execute(f"SELECT * FROM {t}").fetchall() 
  pi=[i for i in range(len(bc)) if [d for d in b.execute(f"PRAGMA table_info({t})")][i][5]][0] 
  existing={r[pi] for r in cr} 
  nr=[r for r in br if r[pi] not in existing] 
  if nr: 
    c.executemany(f"INSERT OR IGNORE INTO {t} ({','.join(bc)}) VALUES ({','.join(['?']*len(bc))})",nr) 
    c.commit() 
    print(f"{t}: {len(nr)} rows merged") 
  else: 
    print(f"{t}: no new rows") 
c.close() 
b.close() 
