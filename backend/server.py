import json, math, os, sqlite3, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB=os.path.join(ROOT,'data','landguard.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

SEED=[
 {'id':1,'name':'Tawang Corridor','district':'Tawang, Arunachal Pradesh','lat':27.586,'lon':91.859,'rainfall':142,'soil':78,'slope':72,'susceptibility':84,'exposure':68,'status':'Critical'},
 {'id':2,'name':'Gangtok–Rangpo Road','district':'Gangtok, Sikkim','lat':27.331,'lon':88.613,'rainfall':118,'soil':69,'slope':66,'susceptibility':76,'exposure':82,'status':'High'},
 {'id':3,'name':'Aizawl Bypass','district':'Aizawl, Mizoram','lat':23.736,'lon':92.718,'rainfall':96,'soil':58,'slope':61,'susceptibility':69,'exposure':74,'status':'Moderate'},
 {'id':4,'name':'Kohima–Imphal Corridor','district':'Kohima, Nagaland','lat':25.675,'lon':94.109,'rainfall':131,'soil':73,'slope':78,'susceptibility':81,'exposure':77,'status':'High'},
 {'id':5,'name':'Shillong Fringe','district':'East Khasi Hills, Meghalaya','lat':25.578,'lon':91.893,'rainfall':88,'soil':52,'slope':48,'susceptibility':57,'exposure':63,'status':'Moderate'},
]

def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
 c=db(); c.execute('''CREATE TABLE IF NOT EXISTS cells(id INTEGER PRIMARY KEY,name TEXT,district TEXT,lat REAL,lon REAL,rainfall REAL,soil REAL,slope REAL,susceptibility REAL,exposure REAL,status TEXT)''')
 c.execute('''CREATE TABLE IF NOT EXISTS reports(id INTEGER PRIMARY KEY AUTOINCREMENT,location TEXT,lat REAL,lon REAL,category TEXT,description TEXT,created TEXT,status TEXT,offline INTEGER)''')
 c.execute('''CREATE TABLE IF NOT EXISTS alerts(id INTEGER PRIMARY KEY AUTOINCREMENT,cell_id INTEGER,level TEXT,message TEXT,created TEXT,status TEXT)''')
 if c.execute('SELECT COUNT(*) FROM cells').fetchone()[0]==0:
  c.executemany('INSERT INTO cells VALUES (:id,:name,:district,:lat,:lon,:rainfall,:soil,:slope,:susceptibility,:exposure,:status)',SEED)
 c.commit(); c.close()

def score(x):
 risk=0.24*min(x['rainfall']/150*100,100)+0.18*x['soil']+0.18*x['slope']+0.25*x['susceptibility']+0.15*x['exposure']
 evidence=(0.35*min(x['rainfall']/150*100,100)+0.25*x['soil']+0.2*x['susceptibility']+0.2*x['slope'])
 confidence=min(98,max(42, evidence - abs(x['soil']-x['susceptibility'])*0.35 + 8))
 return round(risk,1), round(confidence,1)

def json_out(h, data, code=200):
 b=json.dumps(data).encode(); h.send_response(code); h.send_header('Content-Type','application/json'); h.send_header('Content-Length',str(len(b))); h.end_headers(); h.wfile.write(b)

class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  path=urlparse(path).path
  if path=='/' or path=='/index.html': return os.path.join(ROOT,'frontend','index.html')
  return os.path.join(ROOT,'frontend',path.lstrip('/'))
 def do_GET(self):
  p=urlparse(self.path).path
  if p=='/api/health': return json_out(self,{'ok':True,'service':'LandGuard AI API','mode':'demo'})
  if p=='/api/cells':
   c=db(); rows=[dict(r) for r in c.execute('SELECT * FROM cells').fetchall()]; c.close()
   for r in rows: r['risk'],r['confidence']=score(r)
   return json_out(self,{'cells':rows})
  if p=='/api/reports':
   c=db(); rows=[dict(r) for r in c.execute('SELECT * FROM reports ORDER BY id DESC').fetchall()]; c.close(); return json_out(self,{'reports':rows})
  if p=='/api/alerts':
   c=db(); rows=[dict(r) for r in c.execute('SELECT * FROM alerts ORDER BY id DESC').fetchall()]; c.close(); return json_out(self,{'alerts':rows})
  return super().do_GET()
 def do_POST(self):
  p=urlparse(self.path).path; n=int(self.headers.get('Content-Length','0')); raw=self.rfile.read(n)
  try: data=json.loads(raw or '{}')
  except: return json_out(self,{'error':'Invalid JSON'},400)
  if p=='/api/reports':
   import datetime
   c=db(); c.execute('INSERT INTO reports(location,lat,lon,category,description,created,status,offline) VALUES(?,?,?,?,?,?,?,?)',(data.get('location','Unknown'),float(data.get('lat',0)),float(data.get('lon',0)),data.get('category','Other'),data.get('description',''),datetime.datetime.utcnow().isoformat(timespec='seconds')+'Z','Received',int(bool(data.get('offline',False))))); c.commit(); rid=c.execute('SELECT last_insert_rowid()').fetchone()[0]; c.close(); return json_out(self,{'ok':True,'id':rid})
  if p=='/api/alerts':
   import datetime
   c=db(); c.execute('INSERT INTO alerts(cell_id,level,message,created,status) VALUES(?,?,?,?,?)',(data.get('cell_id'),data.get('level','High'),data.get('message','Review required'),datetime.datetime.utcnow().isoformat(timespec='seconds')+'Z','Active')); c.commit(); aid=c.execute('SELECT last_insert_rowid()').fetchone()[0]; c.close(); return json_out(self,{'ok':True,'id':aid})
  return json_out(self,{'error':'Not found'},404)

if __name__=='__main__':
 init(); print('LandGuard AI running at http://localhost:8000'); ThreadingHTTPServer(('0.0.0.0',8000),Handler).serve_forever()
