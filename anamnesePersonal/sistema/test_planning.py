import io
import json
import unittest
import zipfile
import test_app as base
from app import app, db, now


class PlanningTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base.SystemTest.setUpClass.__func__(cls)

    def post(self, client, path, data):
        token=client.get('/api/session').json['csrf']
        return client.post('/api'+path,json=data,headers={'X-CSRF-Token':token})

    def setUp(self):
        self.student,_,self.uid=self.students[0]
        self.peer=self.students[1][0]
        self.payload={'days':[{'id':'a','title':'Treino A','weekdays':[0,2], 'exercises':[{'name':'Remada','sets':'3','reps':'10','rest':'60s','notes':'Controle o movimento'}]},
                              {'id':'b','title':'Treino B','weekdays':[4], 'exercises':[{'name':'Agachamento','sets':'4','reps':'8','rest':'90s'}]}]}
        r=self.post(self.a,'/entries',{'kind':'workout','title':'Ficha inicial','target':self.uid,'payload':self.payload})
        self.assertEqual(r.status_code,201,r.json)
        self.eid=r.json['id']

    def record(self,**overrides):
        data={'day_id':'a','plan_version':1,'logs':[{'done':True,'name':'Adulterado','weight':'20'}], 'rpe':7,'mood':'bem','pain':True,'pain_details':'Joelho','feeling':'puxado'}
        data.update(overrides)
        return self.post(self.student,f'/entries/{self.eid}/receipt',{'status':'Concluído','body':json.dumps(data)})

    def get_entry(self):
        return next(e for e in self.student.get('/api/entries').json if e['id']==self.eid)

    def edit(self,payload=None,version=1):
        return self.post(self.a,f'/entries/{self.eid}/edit',{'title':'Ficha revisada','body':'Novo ciclo','payload':payload or self.payload,'expected_version':version})

    def test_versions_keep_original_session_and_detect_stale_clients(self):
        self.assertEqual(self.record().status_code,200)
        before=self.get_entry()['history'][0]['body']
        self.payload['days'][0]['exercises'][0]['name']='Supino'
        self.payload['days'][0]['exercises'][0]['sets']='5'
        self.assertEqual(self.edit().status_code,200)
        e=self.get_entry()
        self.assertEqual(e['payload']['version'],2)
        self.assertEqual(e['history'][0]['body'],before)
        original=json.loads(before)
        self.assertEqual(original['logs'][0]['name'],'Remada')
        self.assertEqual(original['logs'][0]['sets'],'3')
        self.assertEqual(original['plan_snapshot']['title'],'Ficha inicial')
        self.assertEqual(self.edit().status_code,409)
        self.assertEqual(self.record().status_code,409)
        self.assertEqual(self.record(plan_version=2).status_code,200)
        self.assertEqual(json.loads(self.get_entry()['history'][0]['body'])['logs'][0]['name'],'Supino')
        versions=self.a.get(f'/api/entries/{self.eid}/versions').json
        self.assertEqual(versions[0]['payload']['days'][0]['exercises'][0]['name'],'Remada')
        self.assertEqual(self.student.get(f'/api/entries/{self.eid}/versions').status_code,403)

    def test_days_repeat_and_feedback_validates(self):
        self.assertEqual(self.record().status_code,200)
        self.assertEqual(self.record().status_code,200)
        self.assertEqual(self.record(day_id='b').status_code,200)
        self.assertEqual(len(self.get_entry()['history']),3)
        self.assertEqual(json.loads(self.get_entry()['history'][0]['body'])['day_title'],'Treino B')
        for extra in ({'day_id':'unknown'},{'rpe':11},{'rpe':1.5},{'pain':'yes'},{'logs':[{'done':True,'weight':'NaN'}]}):
            self.assertEqual(self.record(**extra).status_code,400)
        self.payload['active']=False
        self.assertEqual(self.edit().status_code,200)
        self.assertEqual(self.record(plan_version=2).status_code,409)
        self.assertEqual(len(self.get_entry()['history']),3)

    def test_notes_isolation_revisions_and_no_export_leak(self):
        route=f'/students/{self.uid}/notes'
        secret='NOTA_INTERNA_NAO_EXPORTAR'
        r=self.post(self.a,route,{'body':secret});self.assertEqual(r.status_code,201)
        nid=r.json['id']
        self.assertEqual(self.student.get('/api'+route).status_code,403)
        self.assertEqual(self.post(self.peer,route,{'body':'bad'}).status_code,403)
        self.assertEqual(self.post(self.a,route+f'/{nid}',{'body':'Revisada','version':1}).status_code,200)
        self.assertEqual(self.post(self.a,route+f'/{nid}',{'body':'Perdida','version':1}).status_code,409)
        self.assertNotIn(secret,self.student.get('/api/entries').get_data(as_text=True))
        export=self.student.get(f'/api/export/{self.uid}')
        self.assertNotIn(secret,export.get_data(as_text=True));export.close()
        with app.app_context():
            self.assertEqual(db().execute('SELECT body FROM coach_note_revisions WHERE note_id=?',(nid,)).fetchone()[0],secret)

    def test_evaluations_repeat_dates_and_validation(self):
        payload={'template_id':'monthly','measured_at':'2026-08-14','values':{'weight':'70.5','pain_score':0}}
        for _ in range(2):
            r=self.post(self.student,'/evaluations',payload);self.assertEqual(r.status_code,201,r.json)
        entries=[e for e in self.student.get('/api/entries').json if e['payload'].get('measured_at')=='2026-08-14']
        self.assertGreaterEqual(len(entries),2)
        self.assertEqual(entries[0]['payload']['pain_score'],0)
        self.assertEqual(entries[0]['payload']['measured_at'],'2026-08-14')
        for values in ({},{'weight':'nan'},{'fat':101},{'weight':True}):
            self.assertEqual(self.post(self.student,'/evaluations',{**payload,'values':values}).status_code,400)
        self.assertEqual(self.post(self.student,'/evaluations',{**payload,'measured_at':'2099-01-01'}).status_code,400)
        self.assertEqual(self.post(self.a,'/evaluations',{**payload,'target':[]}).status_code,400)

    def test_other_professional_cannot_access_notes_versions_reports(self):
        with app.app_context():
            other_id=db().execute("INSERT INTO users(name,email,password,role,created) VALUES(?,?,?,'admin',?)",('Outro','plan-other@example.test','unused',now())).lastrowid
            db().commit()
        other=app.test_client()
        with other.session_transaction() as session:session['uid']=other_id
        for path in (f'/students/{self.uid}/notes',f'/entries/{self.eid}/versions',f'/entries/{self.eid}/report.pdf'):
            self.assertEqual(other.get('/api'+path).status_code,404)
        self.assertEqual(self.post(other,'/evaluations',{'template_id':'monthly','target':self.uid,'measured_at':'2026-08-14','values':{'weight':70}}).status_code,404)

    def test_pdf_word_are_real_documents_and_private(self):
        for fmt in ('pdf','docx'):
            url=f'/api/entries/{self.eid}/report.{fmt}'
            self.assertEqual(self.peer.get(url).status_code,404)
            self.assertEqual(app.test_client().get(url).status_code,401)
            r=self.student.get(url);self.assertEqual(r.status_code,200)
            raw=r.data;r.close()
            if fmt=='pdf':self.assertTrue(raw.startswith(b'%PDF-'))
            else:
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    xml=z.read('word/document.xml').decode()
                    self.assertIn('Remada',xml);self.assertIn('Treino B',xml)

    def test_workout_limits_and_csrf(self):
        self.assertEqual(self.a.post('/api/evaluations',json={}).status_code,403)
        for days in ([],[{'title':'Vazio','exercises':[]}],[{'id':'x','title':'Dia','weekdays':[7],'exercises':[{'name':'A'}]}]):
            r=self.post(self.a,'/entries',{'kind':'workout','title':'Inválida','target':self.uid,'payload':{'days':days}})
            self.assertEqual(r.status_code,400)


if __name__=='__main__':unittest.main(verbosity=2)
