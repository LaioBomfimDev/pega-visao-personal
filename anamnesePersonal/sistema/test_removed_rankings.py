import unittest
import test_app as base
from app import app, db, now


class RemovedRankingsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):base.SystemTest.setUpClass.__func__(cls)

    def test_old_authorizations_cannot_publish_scores_or_profiles(self):
        owner, token, uid = self.students[0]
        peer = self.students[1][0]
        with app.app_context():
            db().execute('INSERT INTO ranking_settings VALUES(1,1)')
            db().execute('INSERT INTO ranking_consent VALUES(?,?,1)', (uid, 'Apelido antigo'))
            db().execute("INSERT INTO user_profiles(user_id,public_key,shared,bio) VALUES(?,?,1,'Bio antiga')", (uid, 'old-key'))
            gid = db().execute("INSERT INTO goals(professional_id,title,total,start,end,public,created) VALUES(1,'Antiga',10,'2026-09-01','2026-09-30',1,?)", (now(),)).lastrowid
            db().commit()
        self.assertEqual(peer.get('/api/rankings').status_code, 410)
        self.assertEqual(peer.get('/api/profiles/old-key').status_code, 404)
        self.assertEqual(peer.get('/api/profiles/old-key/photo').status_code, 404)
        self.assertEqual(peer.get('/api/goals').json, [])
        self.assertEqual(peer.get('/api/journey/team').json, [])
        for path in ('/privacy/settings', '/privacy/consent', f'/goals/{gid}/consent', f'/goals/{gid}/visibility'):
            response = owner.post('/api'+path,json={'enabled':True,'attendance':True,'accepted':True,'confirmed':True},headers={'X-CSRF-Token':token})
            self.assertEqual(response.status_code,410)
        self.assertEqual(owner.post('/api/profile',json={'shared':True,'confirmed':True},headers={'X-CSRF-Token':token}).status_code,400)
        self.assertEqual(set(owner.get('/api/privacy').json), {'activity'})
        self.assertEqual(self.a.post('/api/goals',json={'public':True},headers={'X-CSRF-Token':self.t}).status_code,410)


if __name__=='__main__':unittest.main(verbosity=2)
