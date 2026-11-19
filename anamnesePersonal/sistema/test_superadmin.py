import os,tempfile,unittest
os.environ['ABEL_DATA_DIR']=tempfile.mkdtemp(prefix='super-tests-')
from app import app,db
class SuperTest(unittest.TestCase):
 def test_full_lifecycle_and_isolation(self):
  def client():return app.test_client()
  def post(c,path,data):return c.post('/api'+path,json=data,headers={'X-CSRF-Token':c.get('/api/session').json['csrf']})
  def register(c,url):return post(c,'/register',{'token':url.split('convite=')[1],'password':'test-password-123'})
  a=client();self.assertEqual(post(a,'/setup',{'name':'Abel','email':'a@example.com','password':'test-password-123'}).status_code,200)
  inv=post(a,'/invites',{'name':'Student A','email':'sa@example.com','mode':'On-line'}).json
  sa=client();self.assertEqual(register(sa,inv['url']).status_code,200);aid=sa.get('/api/session').json['user']['id']
  eid=post(a,'/entries',{'kind':'instruction','title':'Equipe A','target':aid,'body':'Orientação privada'}).json['id']
  root=client();post(root,'/login',{'email':'a@example.com','password':'test-password-123'})
  self.assertEqual(post(root,'/super-bootstrap',{'current':'test-password-123','name':'Central','email':'root@example.com','password':'root-password-123'}).status_code,200)
  self.assertEqual(a.get('/api/super/professionals').status_code,403)
  inv=post(root,'/super/invites',{'name':'Prof B','email':'b@example.com'}).json
  b=client();self.assertTrue(register(b,inv['url']).json['pending'])
  self.assertEqual(post(b,'/login',{'email':'b@example.com','password':'test-password-123'}).status_code,403)
  bid=next(p['id'] for p in root.get('/api/super/professionals').json if p['email']=='b@example.com')
  self.assertEqual(post(root,f'/super/professionals/{bid}/status',{'status':'active'}).status_code,200)
  self.assertEqual(post(b,'/login',{'email':'b@example.com','password':'test-password-123'}).status_code,200)
  self.assertEqual(b.get('/api/users').json,[]);self.assertEqual(b.get('/api/entries').json,[])
  self.assertEqual(post(b,f'/entries/{eid}/receipt',{'status':'Avaliado'}).status_code,404)
  self.assertEqual(b.get(f'/api/export/{aid}').status_code,403)
  self.assertEqual(post(b,'/entries',{'kind':'instruction','title':'Cross','target':aid}).status_code,400)
  inv=post(b,'/invites',{'name':'Student B','email':'sb@example.com','mode':'On-line'}).json
  sb=client();self.assertEqual(register(sb,inv['url']).status_code,200)
  self.assertEqual(sb.get('/api/entries').json,[])
  self.assertEqual(root.get('/api/entries').json,[])
  self.assertEqual(post(root,'/entries',{'kind':'progress','title':'x'}).status_code,403)
  self.assertEqual(post(root,f'/super/professionals/{bid}/status',{'status':'blocked'}).status_code,200)
  self.assertEqual(b.get('/api/users').status_code,401);self.assertEqual(sb.get('/api/entries').status_code,401)
  post(root,f'/super/professionals/{bid}/status',{'status':'active'})
  self.assertEqual(b.get('/api/users').status_code,401)
  post(b,'/login',{'email':'b@example.com','password':'test-password-123'})
  url=post(root,f'/super/professionals/{bid}/reset',{}).json['url'];token=url.split('redefinir=')[1]
  anon=client();self.assertEqual(post(anon,'/reset-password',{'token':token,'password':'new-password-123'}).status_code,200)
  self.assertEqual(post(anon,'/reset-password',{'token':token,'password':'new-password-456'}).status_code,400)
  self.assertEqual(b.get('/api/users').status_code,401)
  self.assertEqual(post(b,'/login',{'email':'b@example.com','password':'new-password-123'}).status_code,200)
  self.assertGreater(len(root.get('/api/super/audit').json),4)
if __name__=='__main__':unittest.main(verbosity=2)
