from flask import Flask, request, session, g, jsonify, abort, send_file, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from pathlib import Path
from datetime import datetime, timezone, timedelta
import sqlite3, json, os, secrets, hashlib, io, re, time
from planning import normalize_workout, session_record
from PIL import Image

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get('ABEL_DATA_DIR', '/tmp/AbelAcompanhamento' if os.environ.get('VERCEL') else str(Path.home() / 'AppData/Local/AbelAcompanhamento')))
try:
 DATA.mkdir(parents=True, exist_ok=True)
 (DATA/'media').mkdir(exist_ok=True)
except OSError:
 DATA = Path('/tmp/AbelAcompanhamento')
 DATA.mkdir(parents=True, exist_ok=True)
 (DATA/'media').mkdir(exist_ok=True)
secret_file = DATA/'session.key'
if os.environ.get('ABEL_SECRET_KEY'):
 _secret = os.environ['ABEL_SECRET_KEY']
elif os.environ.get('VERCEL'):
 _secret = hashlib.sha256((os.environ.get('VERCEL_PROJECT_ID','') + 'abel-acompanhamento-prod').encode()).hexdigest()
else:
 if not secret_file.exists(): secret_file.write_text(secrets.token_hex(32))
 _secret = secret_file.read_text()
app = Flask(__name__, static_folder=str(ROOT/'static'))
app.config.update(SECRET_KEY=_secret, MAX_CONTENT_LENGTH=12*1024*1024,
 SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.getenv('ABEL_HTTPS')=='1' or bool(os.getenv('VERCEL')),
 PERMANENT_SESSION_LIFETIME=timedelta(days=7), TRUSTED_HOSTS=None if os.getenv('ABEL_HOSTS')=='*' else os.getenv('ABEL_HOSTS','localhost,127.0.0.1,.vercel.app').split(','))

def db():
 if 'db' not in g:
  g.db=sqlite3.connect(DATA/'abel.sqlite', timeout=15);g.db.row_factory=sqlite3.Row;g.db.execute('PRAGMA foreign_keys=ON')
 return g.db
@app.teardown_appcontext
def close(_):
 if 'db' in g:g.db.close()
def rows(sql,args=()):return [dict(x) for x in db().execute(sql,args).fetchall()]
def one(sql,args=()):
 r=db().execute(sql,args).fetchone();return dict(r) if r else None
def now():return datetime.now(timezone.utc).isoformat()
def insert(sql,args=()):return db().execute(sql,args).lastrowid

def init():
 with app.app_context():
  db().executescript('''
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL,role TEXT NOT NULL,mode TEXT NOT NULL DEFAULT 'On-line',created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS invites(id INTEGER PRIMARY KEY,token TEXT UNIQUE NOT NULL,email TEXT NOT NULL,name TEXT NOT NULL,mode TEXT NOT NULL,expires TEXT NOT NULL,used INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY,kind TEXT NOT NULL,author INTEGER NOT NULL REFERENCES users(id),target INTEGER REFERENCES users(id),audience TEXT NOT NULL DEFAULT 'private',title TEXT NOT NULL,body TEXT NOT NULL,payload TEXT NOT NULL DEFAULT '{}',created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS reactions(entry_id INTEGER REFERENCES entries(id),user_id INTEGER REFERENCES users(id),PRIMARY KEY(entry_id,user_id));
CREATE TABLE IF NOT EXISTS receipts(entry_id INTEGER REFERENCES entries(id),user_id INTEGER REFERENCES users(id),status TEXT NOT NULL,body TEXT DEFAULT '',created TEXT NOT NULL,PRIMARY KEY(entry_id,user_id,status));
CREATE TABLE IF NOT EXISTS activity_logs(id INTEGER PRIMARY KEY,entry_id INTEGER REFERENCES entries(id),user_id INTEGER REFERENCES users(id),body TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS media(id TEXT PRIMARY KEY,entry_id INTEGER NOT NULL REFERENCES entries(id),mime TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),entry_id INTEGER REFERENCES entries(id),title TEXT NOT NULL,seen INTEGER DEFAULT 0,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS revisions(id INTEGER PRIMARY KEY,entry_id INTEGER REFERENCES entries(id),author INTEGER REFERENCES users(id),snapshot TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS attempts(key TEXT PRIMARY KEY,count INTEGER NOT NULL,started REAL NOT NULL);
''')
  for table, columns in {'users': [('professional_id','INTEGER REFERENCES users(id)'),('status',"TEXT NOT NULL DEFAULT 'active'"),('session_version','INTEGER NOT NULL DEFAULT 0')], 'invites':[('professional_id','INTEGER REFERENCES users(id)'),('role',"TEXT NOT NULL DEFAULT 'student'")], 'entries':[('professional_id','INTEGER REFERENCES users(id)')]}.items():
   existing={r['name'] for r in rows('PRAGMA table_info('+table+')')}
   for name,definition in columns:
    if name not in existing:db().execute('ALTER TABLE '+table+' ADD COLUMN '+name+' '+definition)
  db().executescript('''CREATE TABLE IF NOT EXISTS support_audit(id INTEGER PRIMARY KEY,actor INTEGER,target INTEGER,action TEXT,created TEXT);
CREATE TABLE IF NOT EXISTS password_resets(token TEXT PRIMARY KEY,user_id INTEGER REFERENCES users(id),expires TEXT,used INTEGER DEFAULT 0);''')
  legacy=one("SELECT id FROM users WHERE role='admin' ORDER BY id LIMIT 1")
  if legacy:
   db().execute("UPDATE users SET professional_id=? WHERE role='student' AND professional_id IS NULL",(legacy['id'],))
   db().execute("UPDATE invites SET professional_id=? WHERE professional_id IS NULL AND role='student'",(legacy['id'],))
   db().execute("UPDATE entries SET professional_id=COALESCE((SELECT CASE WHEN role='admin' THEN id ELSE professional_id END FROM users WHERE id=entries.author),?) WHERE professional_id IS NULL",(legacy['id'],))
  db().commit()
init()

def user():
 u=one('SELECT id,name,email,role,mode,created,professional_id,status,session_version FROM users WHERE id=?',(session.get('uid'),))
 if u and (u['status']!='active' or session.get('version',0)!=u['session_version']):u=None
 if u and u['role']=='student' and not one("SELECT id FROM users WHERE id=? AND status='active'",(u['professional_id'],)):u=None
 if not u:abort(401,description='Entre na sua conta para continuar.')
 return u
def admin():
 u=user()
 if u['role']!='admin':abort(403,description='Esta ação é exclusiva do profissional.')
 return u
def body():
 d=request.get_json(silent=True)
 if not isinstance(d,dict):abort(400,description='Dados inválidos.')
 return d
def text(d,k,required=False,limit=5000):
 v=d.get(k,'')
 if not isinstance(v,str) or len(v)>limit:abort(400,description='Confira o campo '+k)
 v=v.strip()
 if required and not v:abort(400,description='Preencha '+k)
 return v
def email(d):
 v=text(d,'email',True,250).lower()
 if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',v):abort(400,description='Informe um e-mail válido.')
 return v
def password(d):
 v=text(d,'password',True,200)
 if len(v)<10:abort(400,description='Use uma senha com pelo menos 10 caracteres.')
 return generate_password_hash(v)
def login(u):
 session.clear();session['uid']=u['id'];session['version']=one('SELECT session_version FROM users WHERE id=?',(u['id'],))['session_version'];session['csrf']=secrets.token_urlsafe(32);session.permanent=True

def tenant(u):return u['id'] if u['role']=='admin' else u['professional_id']
def visible(e,u):
 if u['role']=='superadmin' or e['professional_id']!=tenant(u):return False
 if u['role']=='admin':return True
 if e['kind']=='post':return False
 return e['author']==u['id'] or e['target']==u['id'] or (e['kind']=='motivation' and e['audience']=='all')

def entry(id,u):
 e=one('SELECT * FROM entries WHERE id=?',(id,))
 if not e or not visible(e,u):abort(404,description='Registro não encontrado.')
 return e
def notify(ids,title,eid):
 for uid in set(ids):insert('INSERT INTO notifications(user_id,entry_id,title,created) VALUES(?,?,?,?)',(uid,eid,title,now()))
def admins():return [tenant(user())]

@app.before_request
def protect():
 if request.method not in ('GET','HEAD','OPTIONS'):
  origin=request.headers.get('Origin')
  allowed={request.host_url.rstrip('/'),'https://'+request.host,'http://'+request.host}
  if origin and origin not in allowed:abort(403,description='Origem inválida.')
  token=session.get('csrf','')
  if not token or not secrets.compare_digest(token,request.headers.get('X-CSRF-Token','')):abort(403,description='Atualize a página para continuar.')
@app.after_request
def headers(r):
 r.headers['X-Content-Type-Options']='nosniff';r.headers['X-Frame-Options']='SAMEORIGIN';r.headers['Referrer-Policy']='same-origin'
 r.headers['Cache-Control']='no-store'
 r.headers['Content-Security-Policy']="default-src 'self'; img-src 'self' blob: data:; style-src 'self' 'unsafe-inline'; script-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'"
 return r
@app.errorhandler(HTTPException)
def http_error(e):return jsonify(error=e.description),e.code
@app.errorhandler(sqlite3.IntegrityError)
def conflict(e):
 db().rollback();return jsonify(error='Este registro já existe. Confira o e-mail ou atualize a página.'),409
@app.get('/')
def index():return send_from_directory(ROOT/'static','index.html')
@app.get('/api/session')
def state():
 if not session.get('csrf'):session['csrf']=secrets.token_urlsafe(32)
 current=None
 if session.get('uid'):
  try:current=user()
  except HTTPException:pass
 return jsonify(super_setup=not one("SELECT id FROM users WHERE role='superadmin'"),csrf=session['csrf'],setup=not one('SELECT id FROM users LIMIT 1'),user=current)
@app.post('/api/setup')
def setup():
 if not os.environ.get('VERCEL') and request.remote_addr not in ('127.0.0.1','::1'):abort(403)
 d=body();p=password(d);mail=email(d);name=text(d,'name',True,100)
 db().execute('BEGIN IMMEDIATE')
 if one('SELECT id FROM users LIMIT 1'):abort(409,description='A conta principal já foi criada.')
 uid=insert('INSERT INTO users(name,email,password,role,created) VALUES(?,?,?,?,?)',(name,mail,p,'admin',now()));db().commit();login({'id':uid});return jsonify(ok=True)
@app.post('/api/login')
def sign_in():
 d=body();mail=email(d);key=hashlib.sha256((request.remote_addr+mail).encode()).hexdigest();a=one('SELECT * FROM attempts WHERE key=?',(key,))
 if a and time.time()-a['started']<900 and a['count']>=8:abort(429,description='Muitas tentativas. Aguarde 15 minutos.')
 u=one('SELECT * FROM users WHERE email=?',(mail,))
 if not u or not check_password_hash(u['password'],text(d,'password',True,200)):
  if not a or time.time()-a['started']>=900:db().execute('INSERT OR REPLACE INTO attempts VALUES(?,1,?)',(key,time.time()))
  else:db().execute('UPDATE attempts SET count=count+1 WHERE key=?',(key,))
  db().commit();abort(401,description='E-mail ou senha incorretos.')
 if u['status']!='active':abort(403,description='Acesso pendente de aprovação ou bloqueado. Procure o suporte.')
 if u['role']=='student' and not one("SELECT id FROM users WHERE id=? AND status='active'",(u['professional_id'],)):abort(403,description='Acesso do profissional indisponível.')
 db().execute('DELETE FROM attempts WHERE key=?',(key,));db().commit();login(u);return jsonify(ok=True)
@app.post('/api/logout')
def logout():session.clear();return jsonify(ok=True)
@app.post('/api/invites')
def invite():
 u=admin();d=body();mail=email(d);name=text(d,'name',True,100);mode=text(d,'mode')
 if mode not in ('On-line','Presencial'):abort(400)
 if one('SELECT id FROM users WHERE email=?',(mail,)):abort(409,description='Já existe um aluno com esse e-mail.')
 token=secrets.token_urlsafe(32)
 db().execute('UPDATE invites SET used=1 WHERE email=?',(mail,))
 insert('INSERT INTO invites(token,email,name,mode,expires,professional_id) VALUES(?,?,?,?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),mail,name,mode,(datetime.now(timezone.utc)+timedelta(days=7)).isoformat(),u['id']));db().commit()
 return jsonify(url=request.host_url+'?convite='+token)
@app.post('/api/register')
def register():
 d=body();p=password(d);token=hashlib.sha256(text(d,'token',True,200).encode()).hexdigest()
 db().execute('BEGIN IMMEDIATE');inv=one('SELECT * FROM invites WHERE token=? AND used=0 AND expires>?',(token,now()))
 if not inv:abort(400,description='Convite inválido, utilizado ou expirado. Solicite outro a Abel.')
 if inv['role']=='student' and not one("SELECT id FROM users WHERE id=? AND status='active'",(inv['professional_id'],)):abort(403)
 uid=insert('INSERT INTO users(name,email,password,role,mode,created,professional_id,status) VALUES(?,?,?,?,?,?,?,?)',(inv['name'],inv['email'],p,inv['role'],inv['mode'],now(),inv['professional_id'],'pending' if inv['role']=='admin' else 'active'))
 db().execute('UPDATE invites SET used=1 WHERE id=?',(inv['id'],))
 notify([inv['professional_id']] if inv['role']=='student' else [x['id'] for x in rows("SELECT id FROM users WHERE role='superadmin'")],'Novo cadastro: '+inv['name'],None)
 db().commit()
 if inv['role']=='student':login({'id':uid})
 return jsonify(ok=True,pending=inv['role']=='admin')
@app.post('/api/password')
def change_password():
 u=user();d=body();saved=one('SELECT password FROM users WHERE id=?',(u['id'],))
 if not check_password_hash(saved['password'],text(d,'current',True,200)):abort(400,description='A senha atual não confere.')
 db().execute('UPDATE users SET password=?,session_version=session_version+1 WHERE id=?',(password(d),u['id']));db().commit();login(u);return jsonify(ok=True)
@app.get('/api/users')
def users():
 u=admin();return jsonify(rows("SELECT id,name,email,mode,created FROM users WHERE role='student' AND professional_id=? ORDER BY name",(u['id'],)))
@app.get('/api/entries')
def list_entries():
 u=user();result=[]
 for e in rows('SELECT e.*,u.name AS author_name FROM entries e JOIN users u ON u.id=e.author ORDER BY e.id DESC'):
  if visible(e,u):
   e['payload']=json.loads(e['payload']);e['media']=rows('SELECT id,mime FROM media WHERE entry_id=?',(e['id'],));e['reactions']=0;e['liked']=False
   e['receipts']=rows('SELECT r.*,u.name FROM receipts r JOIN users u ON u.id=r.user_id WHERE entry_id=?'+('' if u['role']=='admin' else " AND (r.user_id=? OR (u.role='admin' AND r.status='Avaliado'))"),(e['id'],) if u['role']=='admin' else (e['id'],u['id']))
   e['history']=rows('SELECT * FROM activity_logs WHERE entry_id=?'+('' if u['role']=='admin' else ' AND user_id=?')+' ORDER BY id DESC',(e['id'],) if u['role']=='admin' else (e['id'],u['id']))
   for log in e['history']:
    log['messages']=rows('SELECT m.id,m.body,m.created,m.author,u.name,u.role FROM workout_messages m JOIN users u ON u.id=m.author WHERE m.log_id=? ORDER BY m.id',(log['id'],))
   e['revisions']=rows('SELECT id,created FROM revisions WHERE entry_id=? ORDER BY id DESC',(e['id'],))
   result.append(e)
 return jsonify(result)
@app.post('/api/entries')
def create_entry():
 u=user();d=body();kind=text(d,'kind',True,30);aud=text(d,'audience') or 'private';target=d.get('target');payload=d.get('payload',{})
 if u['role']=='superadmin':abort(403)
 if kind=='post' and u['role']=='student':abort(403)
 if kind not in ('motivation','instruction','workout','progress','checkin','assessment','appointment','resource'):abort(400)
 if not isinstance(payload,dict) or len(json.dumps(payload))>100000:abort(400)
 if u['role']!='admin':
  if kind not in ('progress','checkin','assessment'):abort(403)
  target=u['id'];aud='private'
 if aud not in ('private','all','On-line','Presencial'):abort(400)
 if target:
  if not isinstance(target,int) or not one("SELECT id FROM users WHERE id=? AND role='student' AND professional_id=?",(target,tenant(u))):abort(400)
 if kind!='motivation':
  aud='private'
  if not target:abort(400,description='Selecione o aluno.')
 else:
  if d.get('confirmed') is not True:abort(400,description='Confirme que a mensagem não contém dados de alunos.')
  aud='all';target=None;payload={'day':datetime.now(timezone(timedelta(hours=-3))).date().isoformat()}
  db().execute('BEGIN IMMEDIATE')
  if one("SELECT id FROM entries WHERE professional_id=? AND kind='motivation' AND json_extract(payload,'$.day')=?",(tenant(u),payload['day'])):abort(409,description='A mensagem de hoje já foi enviada. Você pode editá-la em Mensagens.')
 if kind=='workout':payload=normalize_workout(payload)
 if kind=='assessment':
  sections=payload.get('sections')
  if not isinstance(sections,list) or not 1<=len(sections)<=10:abort(400)
  for sec in sections:
   if not isinstance(sec,dict) or not isinstance(sec.get('title'),str) or not isinstance(sec.get('rows'),list) or len(sec['rows'])>60:abort(400)
   for row in sec['rows']:
    if not isinstance(row,dict) or any(not isinstance(row.get(key),str) for key in ('label','value')):abort(400)
 if kind=='appointment':
  try:
   start=datetime.fromisoformat(payload.get('datetime','').replace('Z','+00:00'))
   if not start.tzinfo:raise ValueError()
  except (ValueError,TypeError,AttributeError):abort(400,description='Informe data e horário válidos.')
  if not isinstance(payload.get('place'),str) or len(payload['place'])>500:abort(400)
 if kind=='progress':
  for key in ('weight','waist'):
   if payload.get(key) not in (None,''):
    try:n=float(payload[key])
    except (ValueError,TypeError):abort(400)
    if not 0<n<600:abort(400)
 if kind=='checkin':
  for key in ('energy','difficulty'):
   try:n=int(payload.get(key,0))
   except (ValueError,TypeError):abort(400)
   if not 1<=n<=5:abort(400)
 title=text(d,'title',True,180);content=text(d,'body',False,20000)
 eid=insert('INSERT INTO entries(kind,author,target,audience,title,body,payload,created,professional_id) VALUES(?,?,?,?,?,?,?,?,?)',(kind,u['id'],target,aud,title,content,json.dumps(payload,ensure_ascii=False),now(),tenant(u)))
 if u['role']!='admin':recipients=admins()
 elif target:recipients=[target]
 else:recipients=[x['id'] for x in rows("SELECT id FROM users WHERE role='student' AND professional_id=?"+(' AND mode=?' if aud!='all' else ''),(tenant(u),aud) if aud!='all' else (tenant(u),))]
 notify(recipients,('Novo registro: ' if u['role']!='admin' else u['name']+' publicou: ')+title,eid);db().commit();return jsonify(id=eid),201
@app.post('/api/entries/<int:eid>/edit')
def edit_entry(eid):
 u=admin();d=body();db().execute('BEGIN IMMEDIATE');e=entry(eid,u)
 if e['author']!=u['id']:abort(403)
 title=text(d,'title',True,180);content=text(d,'body',False,20000);payload=json.loads(e['payload'])
 if e['kind']=='workout':
  version=payload.get('version',1)
  if 'payload' in d and d.get('expected_version')!=version:abort(409,description='A ficha mudou. Reabra o editor para carregar a versão atual.')
  payload=normalize_workout(d.get('payload',payload),version+1)
 if e['kind']=='appointment':
  try:
   start=datetime.fromisoformat(text(d,'datetime',True,100).replace('Z','+00:00'))
   if not start.tzinfo:raise ValueError()
  except ValueError:abort(400,description='Informe uma data válida.')
  payload.update(datetime=start.isoformat(),place=text(d,'place',True,500))
 insert('INSERT INTO revisions(entry_id,author,snapshot,created) VALUES(?,?,?,?)',(eid,u['id'],json.dumps(e),now()))
 db().execute('UPDATE entries SET title=?,body=?,payload=? WHERE id=?',(title,content,json.dumps(payload),eid))
 recipients=[e['target']] if e['target'] else [x['id'] for x in rows("SELECT id FROM users WHERE role='student' AND professional_id=?"+(' AND mode=?' if e['audience']!='all' else ''),(tenant(u),e['audience']) if e['audience']!='all' else (tenant(u),))]
 notify(recipients,'Atualização de '+u['name']+': '+title,eid);db().commit();return jsonify(ok=True)
@app.post('/api/entries/<int:eid>/reaction')
def reaction(eid):
 user();abort(410,description='Reações da comunidade foram removidas.')
@app.post('/api/entries/<int:eid>/receipt')
def receipt(eid):
 u=user();db().execute('BEGIN IMMEDIATE');e=entry(eid,u);d=body();status=text(d,'status',True,30);note=text(d,'body',False,20000)
 if status not in ('Lido','Concluído','Solicitou revisão','Avaliado'):abort(400)
 if u['role']=='admin':
  if status!='Avaliado':abort(400)
  recipient=e['target'] or e['author']
 else:
  if e['kind'] not in ('instruction','workout','appointment','resource') or status=='Avaliado':abort(403)
  recipient=e['author']
 if status=='Concluído' and e['kind']=='workout':
  try:
   record=json.loads(note)
   if not isinstance(record,dict):raise ValueError()
  except (ValueError,TypeError):abort(400,description='Confira o registro do treino.')
  record=session_record(e,record);logs=record['logs'];note=json.dumps(record,ensure_ascii=False)
 db().execute('INSERT INTO receipts VALUES(?,?,?,?,?) ON CONFLICT(entry_id,user_id,status) DO UPDATE SET status=excluded.status,body=excluded.body,created=excluded.created',(eid,u['id'],status,note,now()));
 if e['kind']=='workout' and status=='Concluído':insert('INSERT INTO activity_logs(entry_id,user_id,body,created) VALUES(?,?,?,?)',(eid,u['id'],note,now()))
 message=u['name']+': '+status
 if e['kind']=='workout' and status=='Concluído':message=u['name']+(' registrou um treino completo' if all(x['done'] for x in logs) else ' registrou parte do treino')
 notify([recipient],message,eid);db().commit();return jsonify(ok=True)
@app.post('/api/entries/<int:eid>/media')
def upload(eid):
 u=user();e=entry(eid,u)
 if e['kind'] in ('post','motivation'):abort(403,description='Este tipo de mensagem não aceita imagens.')
 if e['author']!=u['id']:abort(403)
 if len(rows('SELECT id FROM media WHERE entry_id=?',(eid,)))>=4:abort(400,description='Limite de quatro imagens por registro.')
 f=request.files.get('file')
 if not f:abort(400,description='Escolha uma imagem.')
 try:
  img=Image.open(f.stream)
  if img.width*img.height>25000000:abort(400,description='Imagem muito grande.')
  img.load()
  img.thumbnail((2000,2000));out=io.BytesIO();img.convert('RGB').save(out,'JPEG',quality=88)
 except HTTPException:raise
 except Exception:abort(400,description='Use uma imagem JPG, PNG ou WebP válida.')
 mid=secrets.token_hex(24);(DATA/'media'/mid).write_bytes(out.getvalue());insert('INSERT INTO media VALUES(?,?,?)',(mid,eid,'image/jpeg'));db().commit();return jsonify(id=mid)
@app.get('/media/<mid>')
def media(mid):
 u=user();m=one('SELECT * FROM media WHERE id=?',(mid,))
 if not m:abort(404)
 entry(m['entry_id'],u);return send_file(DATA/'media'/mid,mimetype=m['mime'])
@app.get('/api/notifications')
def notifications():
 u=user();result=[]
 for n in rows('SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 150',(u['id'],)):
  e=one('SELECT * FROM entries WHERE id=?',(n['entry_id'],)) if n['entry_id'] else None
  if n['entry_id'] and (not e or not visible(e,u)):continue
  result.append(n)
 return jsonify(result)
@app.post('/api/notifications/read')
def read_notifications():
 uid=user()['id'];d=body()
 if d.get('id'):db().execute('UPDATE notifications SET seen=1 WHERE user_id=? AND id=?',(uid,d['id']))
 else:db().execute('UPDATE notifications SET seen=1 WHERE user_id=?',(uid,))
 db().commit();return jsonify(ok=True)
@app.get('/api/export/<int:uid>')
def export(uid):
 u=user()
 if uid!=u['id'] and (u['role']!='admin' or not one("SELECT id FROM users WHERE id=? AND professional_id=? AND role='student'",(uid,u['id']))):abort(403)
 if u['role']=='superadmin':abort(403)
 profile=one('SELECT id,name,email,mode,created FROM users WHERE id=?',(uid,))
 if not profile:abort(404)
 data={'aluno':profile,'registros':rows('SELECT * FROM entries WHERE target=? OR author=?',(uid,uid)), 'autorizacoes':rows('SELECT action,version,created FROM privacy_events WHERE actor=?',(uid,))}
 return send_file(io.BytesIO(json.dumps(data,ensure_ascii=False,indent=2).encode()),mimetype='application/json',as_attachment=True,download_name='acompanhamento.json')
@app.get('/anamnese/<path:name>')
def assessment_page(name):
 user()
 allowed={'index.html','style.css','script.js','vendor/docx-8.2.3.umd.js'}
 if name not in allowed:abort(404)
 return send_from_directory(ROOT/'anamnese',name)


def superadmin():
 u=user()
 if u['role']!='superadmin':abort(403)
 return u
def audit(u,target,action):insert('INSERT INTO support_audit(actor,target,action,created) VALUES(?,?,?,?)',(u['id'],target,action,now()))
@app.post('/api/super-bootstrap')
def super_bootstrap():
 u=admin();d=body()
 if not os.environ.get('VERCEL') and request.remote_addr not in ('127.0.0.1','::1'):abort(403)
 if not check_password_hash(one('SELECT password FROM users WHERE id=?',(u['id'],))['password'],text(d,'current',True,200)):abort(403,description='A senha atual não confere.')
 p=password(d);mail=email(d);name=text(d,'name',True,100)
 db().execute('BEGIN IMMEDIATE')
 if one("SELECT id FROM users WHERE role='superadmin'"):abort(409)
 uid=insert('INSERT INTO users(name,email,password,role,created) VALUES(?,?,?,?,?)',(name,mail,p,'superadmin',now()))
 audit(u,uid,'Criação do SUPERADM');db().commit();login({'id':uid});return jsonify(ok=True)
@app.get('/api/super/professionals')
def professionals():
 superadmin();return jsonify(rows("SELECT id,name,email,status,created,(SELECT count(*) FROM users s WHERE s.professional_id=p.id AND s.role='student') AS students FROM users p WHERE role='admin' ORDER BY name"))
@app.get('/api/super/audit')
def support_logs():
 superadmin();return jsonify(rows('SELECT a.*,u.name AS actor_name,t.name AS target_name FROM support_audit a LEFT JOIN users u ON u.id=a.actor LEFT JOIN users t ON t.id=a.target ORDER BY a.id DESC LIMIT 100'))
@app.post('/api/super/invites')
def professional_invite():
 u=superadmin();d=body();mail=email(d);name=text(d,'name',True,100)
 if one('SELECT id FROM users WHERE email=?',(mail,)):abort(409,description='E-mail já cadastrado.')
 token=secrets.token_urlsafe(32)
 db().execute('UPDATE invites SET used=1 WHERE email=?',(mail,))
 insert("INSERT INTO invites(token,email,name,mode,expires,role) VALUES(?,?,?,'On-line',?,'admin')",(hashlib.sha256(token.encode()).hexdigest(),mail,name,(datetime.now(timezone.utc)+timedelta(days=7)).isoformat()))
 audit(u,None,'Convite de profissional: '+mail);db().commit();return jsonify(url=request.host_url+'?convite='+token)
@app.post('/api/super/professionals/<int:uid>/status')
def professional_status(uid):
 u=superadmin();d=body();status=text(d,'status',True,20)
 if status not in ('active','blocked'):abort(400)
 if not one("SELECT id FROM users WHERE id=? AND role='admin'",(uid,)):abort(404)
 db().execute('UPDATE users SET status=?,session_version=session_version+1 WHERE id=?',(status,uid))
 db().execute('UPDATE users SET session_version=session_version+1 WHERE professional_id=?',(uid,))
 audit(u,uid,'Acesso '+status);db().commit();return jsonify(ok=True)
@app.post('/api/super/professionals/<int:uid>/reset')
def support_reset(uid):
 u=superadmin()
 if not one("SELECT id FROM users WHERE id=? AND role='admin'",(uid,)):abort(404)
 token=secrets.token_urlsafe(32)
 db().execute('UPDATE password_resets SET used=1 WHERE user_id=?',(uid,))
 insert('INSERT INTO password_resets(token,user_id,expires) VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),uid,(datetime.now(timezone.utc)+timedelta(minutes=30)).isoformat()))
 audit(u,uid,'Link de redefinição de senha gerado');db().commit();return jsonify(url=request.host_url+'?redefinir='+token)
@app.post('/api/reset-password')
def reset_password():
 d=body();p=password(d);token=hashlib.sha256(text(d,'token',True,200).encode()).hexdigest()
 db().execute('BEGIN IMMEDIATE');r=one('SELECT * FROM password_resets WHERE token=? AND used=0 AND expires>?',(token,now()))
 if not r:abort(400,description='Link inválido ou expirado. Solicite outro ao suporte.')
 db().execute('UPDATE users SET password=?,session_version=session_version+1 WHERE id=?',(p,r['user_id']))
 db().execute('UPDATE password_resets SET used=1 WHERE user_id=?',(r['user_id'],))
 audit({'id':r['user_id']},r['user_id'],'Senha redefinida');db().commit();session.clear();return jsonify(ok=True)

import sys
from privacy import register as register_privacy
register_privacy(app,sys.modules[__name__])
from profiles import register as register_profiles
register_profiles(app,sys.modules[__name__])
from coaching import register as register_coaching
register_coaching(app,sys.modules[__name__])
from planning import register as register_planning
register_planning(app,sys.modules[__name__])
from reports import register as register_reports
register_reports(app,sys.modules[__name__])
from journey import register as register_journey
register_journey(app,sys.modules[__name__])

if __name__=='__main__':
 from waitress import serve
 print('Abel Acompanhamento: http://'+os.getenv('ABEL_BIND','127.0.0.1')+':'+os.getenv('ABEL_PORT','8766'),flush=True)
 serve(app,host=os.getenv('ABEL_BIND','127.0.0.1'),port=int(os.getenv('ABEL_PORT','8766')))
