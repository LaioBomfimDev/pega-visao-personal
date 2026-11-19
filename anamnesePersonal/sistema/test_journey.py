import io
import unittest
from datetime import date
from unittest.mock import patch
from PIL import Image
import test_app as base
from app import app, db, now


class JourneyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base.SystemTest.setUpClass.__func__(cls)

    def post(self, client, path, data):
        token = client.get('/api/session').json['csrf']
        return client.post('/api' + path, json=data, headers={'X-CSRF-Token': token})

    def setUp(self):
        self.owner, _, self.uid = self.students[0]
        self.peer = self.students[1][0]
        with app.app_context():
            for table in ('workout_messages', 'activity_logs', 'journey_sharing', 'user_profiles'):
                db().execute('DELETE FROM ' + table)
            db().execute("UPDATE users SET status='active' WHERE id=?", (self.uid,))
            db().commit()
        r = self.post(self.a, '/entries', dict(kind='workout', title='Privado', target=self.uid,
                         payload=dict(exercises=[dict(name='Remada', sets='3', reps='10', rest='60s')])))
        self.eid = r.json['id']
        self.seed(['2026-09-01T12:00:00+00:00'])

    def seed(self, stamps):
        with app.app_context():
            for stamp in stamps:
                db().execute('INSERT INTO activity_logs(entry_id,user_id,body,created) VALUES(?,?,?,?)',
                             (self.eid, self.uid, '{"note":"DADO_PRIVADO"}', stamp))
            db().commit()

    def share(self, **kwargs):
        return self.post(self.owner, '/journey', dict(selected=['first'], shared=True, confirmed=True, **kwargs))

    def test_private_default_explicit_consent_and_selected_only(self):
        self.seed(['2026-09-10T12:00:00+00:00'])
        self.assertEqual(self.peer.get('/api/journey/team').json, [])
        j = self.owner.get('/api/journey').json
        self.assertFalse(j['shared'])
        self.assertEqual({m['id'] for m in j['earned']} & {'first', 'return'}, {'first', 'return'})
        self.assertEqual(self.post(self.owner, '/journey', dict(selected=['first'], shared=True)).status_code, 400)
        self.assertEqual(self.share().status_code, 200)
        public = self.peer.get('/api/journey/team').json[0]
        self.assertEqual([m['id'] for m in public['highlights']], ['first'])
        self.assertEqual(public['display_name'], 'Participante')
        self.assertEqual(set(public), {'key', 'display_name', 'bio', 'photo_url', 'highlights'})
        self.assertNotIn('DADO_PRIVADO', str(public))
        self.assertEqual(set(self.owner.get('/api/privacy').json), {'activity'})

    def test_rejects_unearned_duplicates_over_three_and_csrf(self):
        for selected in (['story'], ['first', 'first'], ['first'] * 4, [1], 'first'):
            self.assertEqual(self.post(self.owner, '/journey', dict(selected=selected, shared=False)).status_code, 400)
        self.assertEqual(self.post(self.owner, '/journey', dict(selected=[], shared=True, confirmed=True)).status_code, 400)
        self.assertEqual(self.owner.post('/api/journey', json={}).status_code, 403)
        self.assertEqual(self.post(self.a, '/journey', dict(shared=False)).status_code, 403)

    def test_isolation_and_revocation_including_photos(self):
        raw = io.BytesIO()
        Image.new('RGB', (20, 20), 'green').save(raw, 'PNG'); raw.seek(0)
        token = self.owner.get('/api/session').json['csrf']
        self.owner.post('/api/profile/photo', data={'file': (raw, 'foto.png')}, headers={'X-CSRF-Token': token})
        self.share()
        public = self.peer.get('/api/journey/team').json[0]
        path = '/api/journey/profiles/' + public['key']
        photo = public['photo_url']
        response = self.peer.get(photo)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Cache-Control'], 'no-store'); response.close()
        with app.app_context():
            other_id = db().execute("INSERT INTO users(name,email,password,role,created) VALUES(?,?,?,'admin',?)",
                                  ('Outra equipe', 'journey-other@example.test', 'unused', now())).lastrowid
            db().commit()
        other = app.test_client()
        with other.session_transaction() as s:s['uid'] = other_id
        self.assertEqual(other.get('/api/journey/team').json, [])
        for url in (path, photo):
            self.assertEqual(other.get(url).status_code, 404)
            self.assertEqual(app.test_client().get(url).status_code, 401)
        self.post(self.owner, '/journey', dict(shared=False, selected=['first']))
        self.assertEqual(self.peer.get('/api/journey/team').json, [])
        self.assertEqual(self.peer.get(path).status_code, 404)
        self.assertEqual(self.peer.get(photo).status_code, 404)

    def test_blocked_user_disappears(self):
        self.share()
        key = self.peer.get('/api/journey/team').json[0]['key']
        with app.app_context():
            db().execute("UPDATE users SET status='blocked' WHERE id=?", (self.uid,)); db().commit()
        self.assertEqual(self.peer.get('/api/journey/team').json, [])
        self.assertEqual(self.peer.get('/api/journey/profiles/' + key).status_code, 404)

    def test_dates_pauses_and_unique_days(self):
        self.seed(['2026-09-02T01:00:00+00:00', '2026-09-20T12:00:00+00:00'])
        with patch('journey.today', return_value=date(2026, 9, 15)):
            ids = {m['id'] for m in self.owner.get('/api/journey').json['earned']}
            self.assertNotIn('rhythm', ids)
            self.assertNotIn('return', ids)
        self.seed([f'2026-09-{d:02d}T12:00:00+00:00' for d in (3, 5, 7, 15)])
        with patch('journey.today', return_value=date(2026, 9, 15)):
            before = {m['id'] for m in self.owner.get('/api/journey').json['earned']}
            self.assertTrue({'first', 'rhythm', 'return'} <= before)
        with patch('journey.today', return_value=date(2026, 10, 15)):
            self.assertTrue(before <= {m['id'] for m in self.owner.get('/api/journey').json['earned']})


if __name__ == '__main__':unittest.main(verbosity=2)
