import json,unittest
from datetime import date
from unittest.mock import patch
import test_app as base
from app import app,db,now

class PrivacyTest(base.SystemTest):
 def setUp(self):
  with app.app_context():
   db().execute('DELETE FROM ranking_settings');db().execute('DELETE FROM ranking_consent');db().execute('DELETE FROM goal_members');db().execute('DELETE FROM goals');db().execute('DELETE FROM training_schedule');db().execute('DELETE FROM activity_logs');db().execute("DELETE FROM notifications WHERE entry_id IN (SELECT id FROM entries WHERE kind='motivation')");db().execute("DELETE FROM entries WHERE kind='motivation'");db().commit()
 def sp(self,path,data,index=0):
  c,t,uid=self.students[index];return c.post(path,json=data,headers={'X-CSRF-Token':t})
 def enable(self):self.assertEqual(self.post('/api/privacy/settings',{'enabled':True,'confirmed':True}).status_code,200)
 def accept(self):return self.sp('/api/privacy/consent',{'attendance':True,'confirmed':True,'alias':'Foco 01'})
 def test_private_goal_and_permissions(self):
  gid=self.post('/api/goals',{'title':'Minha meta','target':self.students[0][2],'total':2,'start':'2026-09-01','end':'2026-09-30'}).json['id']
  self.assertEqual(len(self.students[0][0].get('/api/goals').json),1);self.assertEqual(self.students[1][0].get('/api/goals').json,[])
  self.assertEqual(self.sp('/api/privacy/settings',{'enabled':True,'confirmed':True}).status_code,410);self.assertEqual(self.sp('/api/goals',{}).status_code,403);self.assertEqual(self.sp(f'/api/goals/{gid}/consent',{'accepted':True,'confirmed':True}).status_code,410)
 def test_legacy_community_and_reactions_hidden(self):
  with app.app_context():
   eid=db().execute("INSERT INTO entries(kind,author,audience,title,body,created,professional_id) VALUES('post',1,'all','Dado antigo de aluno','privado',?,1)",(now(),)).lastrowid
   db().execute('INSERT INTO notifications(user_id,entry_id,title,created) VALUES(?,?,?,?)',(self.students[0][2],eid,'Dado antigo de aluno',now()));db().commit()
  c=self.students[0][0];self.assertNotIn(eid,[x['id'] for x in c.get('/api/entries').json]);self.assertNotIn(eid,[x['entry_id'] for x in c.get('/api/notifications').json]);self.assertEqual(self.sp(f'/api/entries/{eid}/reaction',{}).status_code,410)
  self.assertEqual(self.post('/api/entries',{'kind':'post','title':'Antigo','audience':'all'}).status_code,400)
 def test_daily_motivation_is_professional_only(self):
  payload={'kind':'motivation','title':'Vamos juntos','body':'Um passo por vez','confirmed':True}
  self.assertEqual(self.sp('/api/entries',payload).status_code,403)
  r=self.post('/api/entries',payload);self.assertEqual(r.status_code,201,r.json);eid=r.json['id'];self.assertEqual(self.post('/api/entries',payload).status_code,409)
  for c,t,uid in self.students:
   e=next(x for x in c.get('/api/entries').json if x['id']==eid);self.assertEqual(e['target'],None);self.assertEqual(e['receipts'],[]);self.assertEqual(e['reactions'],0)
  self.assertEqual(self.sp(f'/api/entries/{eid}/receipt',{'status':'Lido'}).status_code,403)

if __name__=='__main__':unittest.main(verbosity=2)

