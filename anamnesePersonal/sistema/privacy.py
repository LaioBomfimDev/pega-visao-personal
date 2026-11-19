from datetime import datetime, timedelta, timezone, date
import json, secrets
from flask import jsonify, abort

BRASILIA=timezone(timedelta(hours=-3))
CONSENT_VERSION='rankings-v1'

def today():return datetime.now(BRASILIA).date()

def register(app,c):
 with app.app_context():
  c.db().executescript('''
CREATE TABLE IF NOT EXISTS ranking_settings(professional_id INTEGER PRIMARY KEY REFERENCES users(id),enabled INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS ranking_consent(user_id INTEGER PRIMARY KEY REFERENCES users(id),alias TEXT NOT NULL,attendance INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS privacy_events(id INTEGER PRIMARY KEY,actor INTEGER,professional_id INTEGER,action TEXT,version TEXT,created TEXT);
CREATE TABLE IF NOT EXISTS training_schedule(user_id INTEGER PRIMARY KEY REFERENCES users(id),weekdays TEXT NOT NULL,start TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY,professional_id INTEGER REFERENCES users(id),target INTEGER REFERENCES users(id),title TEXT NOT NULL,total INTEGER NOT NULL,start TEXT NOT NULL,end TEXT NOT NULL,public INTEGER NOT NULL DEFAULT 0,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS goal_members(goal_id INTEGER REFERENCES goals(id),user_id INTEGER REFERENCES users(id),accepted INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(goal_id,user_id));
CREATE UNIQUE INDEX IF NOT EXISTS one_motivation_daily ON entries(professional_id,json_extract(payload,'$.day')) WHERE kind='motivation';
''');c.db().commit()
 def member():
  u=c.user()
  if u['role']=='superadmin':abort(403)
  return u
 def days(uid):
  result=set()
  for row in c.rows("SELECT l.created FROM activity_logs l JOIN entries e ON e.id=l.entry_id JOIN users u ON u.id=l.user_id WHERE l.user_id=? AND e.professional_id=u.professional_id AND e.kind='workout'",(uid,)):
   result.add(datetime.fromisoformat(row['created']).astimezone(BRASILIA).date())
  return result
 def activity_summary(uid):
  end=today();done={d for d in days(uid) if d<=end};day=end if end in done else end-timedelta(days=1);current=0
  while day in done:current+=1;day-=timedelta(days=1)
  best=run=0;previous=None
  for day in sorted(done):
   run=run+1 if previous and day==previous+timedelta(days=1) else 1
   best=max(best,run);previous=day
  week=[{'date':(end-timedelta(days=i)).isoformat(),'trained':end-timedelta(days=i) in done,'today':i==0} for i in range(6,-1,-1)]
  return {'daily_streak':current,'best_streak':best,'total_days':len(done),'trained_today':end in done,'week':week}
 @app.get('/api/privacy')
 def privacy():
  u=member()
  return jsonify(activity=activity_summary(u['id']) if u['role']=='student' else None)

 @app.route('/api/rankings',methods=['GET','POST'])
 @app.post('/api/privacy/settings')
 @app.post('/api/privacy/consent')
 @app.post('/api/privacy/revoke-all')
 @app.post('/api/goals/<int:gid>/consent')
 @app.post('/api/goals/<int:gid>/visibility')
 def retired(gid=None):
  member();abort(410,description='Este recurso foi removido.')

 @app.get('/api/goals')
 def private_goals():
  u=member()
  return jsonify(c.rows('SELECT id,target,title,total,start,end FROM goals WHERE professional_id=? AND public=0 AND target IS NOT NULL'+('' if u['role']=='admin' else ' AND target=?'),(c.tenant(u),) if u['role']=='admin' else (c.tenant(u),u['id'])))

 @app.post('/api/goals')
 def create_private_goal():
  u=c.admin();d=c.body()
  if d.get('public',False) is not False:abort(410,description='Metas coletivas foram removidas.')
  target=d.get('target');total=d.get('total');title=c.text(d,'title',True,100)
  if type(total)!=int or not 1<=total<=365:abort(400)
  if type(target)!=int or not c.one("SELECT id FROM users WHERE id=? AND professional_id=? AND role='student'",(target,u['id'])):abort(400)
  try:start=date.fromisoformat(d.get('start',''));end=date.fromisoformat(d.get('end',''))
  except (ValueError,TypeError):abort(400)
  if end<start or (end-start).days>365 or total>(end-start).days+1:abort(400)
  gid=c.insert('INSERT INTO goals(professional_id,target,title,total,start,end,public,created) VALUES(?,?,?,?,?,?,0,?)',(u['id'],target,title,total,start.isoformat(),end.isoformat(),c.now()));c.db().commit();return jsonify(id=gid),201
