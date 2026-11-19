import os,tempfile,unittest,io,json
from pathlib import Path
os.environ['ABEL_DATA_DIR']=tempfile.mkdtemp(prefix='abel-tests-')
from app import app
from PIL import Image
class SystemTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=app.test_client();cls.t=cls.a.get('/api/session').json['csrf']
  r=cls.a.post('/api/setup',json={'name':'Abel Teste','email':'abel@example.com','password':'senha-teste-123'},headers={'X-CSRF-Token':cls.t});assert r.status_code==200,r.json
  cls.t=cls.a.get('/api/session').json['csrf'];cls.students=[]
  for i in range(2):
   r=cls.a.post('/api/invites',json={'name':'Aluno '+str(i),'email':f'aluno{i}@example.com','mode':['On-line','Presencial'][i]},headers={'X-CSRF-Token':cls.t})
   token=r.json['url'].split('convite=')[1];c=app.test_client();t=c.get('/api/session').json['csrf']
   r=c.post('/api/register',json={'token':token,'password':'senha-aluno-123'},headers={'X-CSRF-Token':t});assert r.status_code==200,r.json
   s=c.get('/api/session').json;cls.students.append((c,s['csrf'],s['user']['id']))
 @classmethod
 def post(cls,path,data):return cls.a.post(path,json=data,headers={'X-CSRF-Token':cls.t})
 def make(self,kind='instruction',audience='private',target=None,payload=None):
  return self.post('/api/entries',{'kind':kind,'title':'Registro teste','body':'Descrição','audience':audience,'target':target or self.students[0][2],'payload':payload or {}})
 def test_csrf(self):self.assertEqual(self.a.post('/api/entries',json={}).status_code,403)
 def test_origin(self):self.assertEqual(self.a.post('/api/entries',json={},headers={'X-CSRF-Token':self.t,'Origin':'https://evil.example'}).status_code,403)
 def test_setup_closed(self):self.assertEqual(self.post('/api/setup',{'name':'X','email':'x@example.com','password':'password-123'}).status_code,409)
 def test_student_cannot_admin(self):
  c,t,uid=self.students[0];self.assertEqual(c.get('/api/users').status_code,403);self.assertEqual(c.post('/api/entries',json={'kind':'post','title':'x','audience':'all'},headers={'X-CSRF-Token':t}).status_code,403)
 def test_private_records(self):
  r=self.make();eid=r.json['id'];a,t,uid=self.students[0];b,bt,bid=self.students[1]
  self.assertIn(eid,[e['id'] for e in a.get('/api/entries').json]);self.assertNotIn(eid,[e['id'] for e in b.get('/api/entries').json]);self.assertEqual(b.post(f'/api/entries/{eid}/receipt',json={'status':'Lido'},headers={'X-CSRF-Token':bt}).status_code,404)
 def test_student_cannot_publish_private_data(self):
  c,t,uid=self.students[0];r=c.post('/api/entries',json={'kind':'progress','title':'Peso','audience':'all','target':self.students[1][2],'payload':{'weight':75}},headers={'X-CSRF-Token':t});self.assertEqual(r.status_code,201)
  e=next(x for x in self.a.get('/api/entries').json if x['id']==r.json['id']);self.assertEqual(e['target'],uid);self.assertEqual(e['audience'],'private')
 def test_media_private_and_validated(self):
  eid=self.make().json['id'];buff=io.BytesIO();Image.new('RGB',(10,10),'red').save(buff,'PNG');buff.seek(0)
  r=self.a.post(f'/api/entries/{eid}/media',data={'file':(buff,'test.png')},headers={'X-CSRF-Token':self.t});self.assertEqual(r.status_code,200,r.json)
  url='/media/'+r.json['id'];response=self.students[0][0].get(url);self.assertEqual(response.status_code,200);response.close();self.assertEqual(self.students[1][0].get(url).status_code,404);self.assertEqual(app.test_client().get(url).status_code,401)
  r=self.a.post(f'/api/entries/{eid}/media',data={'file':(io.BytesIO(b'<svg onload="alert(1)"></svg>'),'bad.svg')},headers={'X-CSRF-Token':self.t});self.assertEqual(r.status_code,400)
 def test_workout_history_preserved(self):
  eid=self.make('workout',payload={'exercises':[{'name':'Remada','sets':'3','reps':'10','rest':'60s'}]}).json['id'];c,t,uid=self.students[0]
  for status in ['Concluído','Lido','Concluído']:
   r=c.post(f'/api/entries/{eid}/receipt',json={'status':status,'body':json.dumps({'logs':[{'name':'Remada','weight':'20','done':True}]})},headers={'X-CSRF-Token':t});self.assertEqual(r.status_code,200,r.json)
  e=next(e for e in c.get('/api/entries').json if e['id']==eid);self.assertEqual(len(e['history']),2);self.assertIn('Concluído',[r['status'] for r in e['receipts']])
 def test_notifications(self):
  eid=self.make().json['id'];c,t,uid=self.students[0];n=next(n for n in c.get('/api/notifications').json if n['entry_id']==eid);c.post('/api/notifications/read',json={'id':n['id']},headers={'X-CSRF-Token':t});self.assertEqual(next(x for x in c.get('/api/notifications').json if x['id']==n['id'])['seen'],1)
 def test_export_isolation(self):self.assertEqual(self.students[1][0].get('/api/export/'+str(self.students[0][2])).status_code,403)
 def test_assessment_validation(self):self.assertEqual(self.make('assessment',payload={'sections':'bad'}).status_code,400)
 def test_appointment_validation(self):self.assertEqual(self.make('appointment',payload={'datetime':'bad'}).status_code,400)
 def test_reopen_login(self):
  c=app.test_client();t=c.get('/api/session').json['csrf'];r=c.post('/api/login',json={'email':'abel@example.com','password':'senha-teste-123'},headers={'X-CSRF-Token':t});self.assertEqual(r.status_code,200);self.assertEqual(c.get('/api/session').json['user']['name'],'Abel Teste')
 def test_student_sees_coach_review(self):
  eid=self.make().json['id'];r=self.a.post(f'/api/entries/{eid}/receipt',json={'status':'Avaliado','body':'Orientação de Abel'},headers={'X-CSRF-Token':self.t});self.assertEqual(r.status_code,200)
  e=next(e for e in self.students[0][0].get('/api/entries').json if e['id']==eid);self.assertTrue(any(r['body']=='Orientação de Abel' for r in e['receipts']))
 def test_edit_preserves_version(self):
  eid=self.make().json['id'];r=self.a.post(f'/api/entries/{eid}/edit',json={'title':'Atualizado','body':'Nova orientação'},headers={'X-CSRF-Token':self.t});self.assertEqual(r.status_code,200)
  e=next(e for e in self.a.get('/api/entries').json if e['id']==eid);self.assertEqual(e['title'],'Atualizado');self.assertEqual(len(e['revisions']),1)
  c,t,uid=self.students[0];self.assertEqual(c.post(f'/api/entries/{eid}/edit',json={'title':'Não permitido'},headers={'X-CSRF-Token':t}).status_code,403)
if __name__=='__main__':unittest.main(verbosity=2)
