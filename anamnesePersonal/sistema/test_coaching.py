import json
import unittest
import test_app as base
from app import app, db, now


class CoachingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base.SystemTest.setUpClass.__func__(cls)

    def post(self, client, path, data):
        token = client.get('/api/session').json['csrf']
        return client.post('/api' + path, json=data, headers={'X-CSRF-Token': token})

    def setUp(self):
        self.student, _, self.uid = self.students[0]
        self.peer = self.students[1][0]
        self.eid = self.post(self.a, '/entries', dict(kind='workout', title='Treino A', target=self.uid,
            payload=dict(exercises=[dict(name='Remada', sets='3', reps='10', rest='60s'), dict(name='Agachamento', sets='3', reps='10', rest='60s')]))).json['id']

    def record(self, **extras):
        payload = dict(logs=[dict(name='Nome adulterado', weight='20', done=True), dict(name='Agachamento', weight='', done=False)], note='Hoje precisei parar antes.', feeling='puxado')
        payload.update(extras)
        return self.post(self.student, f'/entries/{self.eid}/receipt', dict(status='Concluído', body=json.dumps(payload)))

    def history(self, client):
        return next(x for x in client.get('/api/entries').json if x['id'] == self.eid)['history']

    def test_feedback_and_partial_record_are_preserved(self):
        self.assertEqual(self.record().status_code, 200)
        log = self.history(self.a)[0]
        data = json.loads(log['body'])
        self.assertEqual(data['feeling'], 'puxado')
        self.assertEqual(sum(x['done'] for x in data['logs']), 1)
        self.assertEqual(data['logs'][0]['name'], 'Remada')
        self.assertEqual(self.record(feeling='desconforto', note='Outra sessão').status_code, 200)
        self.assertEqual(len(self.history(self.a)), 2)
        self.assertEqual(self.history(self.a)[1]['id'], log['id'])

    def test_conversation_is_private_and_linked_to_session(self):
        self.record()
        log_id = self.history(self.a)[0]['id']
        route = f'/workout-sessions/{log_id}/messages'
        self.assertEqual(self.post(self.peer, route, dict(body='Não autorizado')).status_code, 404)
        self.assertEqual(self.post(self.a, route, dict(body='Obrigado por contar. Qual parte ficou mais difícil?')).status_code, 201)
        self.assertEqual(self.post(self.student, route, dict(body='A última série.')).status_code, 201)
        messages = self.history(self.student)[0]['messages']
        self.assertEqual([x['role'] for x in messages], ['admin', 'student'])
        self.assertEqual(messages[1]['body'], 'A última série.')
        self.assertEqual(self.peer.get('/api/entries').json, [])
        self.record()
        self.assertEqual(self.history(self.a)[0]['messages'], [])
        self.assertEqual(len(self.history(self.a)[1]['messages']), 2)
        self.assertTrue(any(n['entry_id'] == self.eid for n in self.student.get('/api/notifications').json))

    def test_validation_and_csrf(self):
        self.assertEqual(self.record(feeling='inventado').status_code, 400)
        self.assertEqual(self.record(note='x'*1601).status_code, 400)
        self.record()
        route = f"/workout-sessions/{self.history(self.a)[0]['id']}/messages"
        self.assertEqual(self.a.post('/api'+route, json=dict(body='Oi')).status_code, 403)
        self.assertEqual(self.post(self.a, route, dict(body='  ')).status_code, 400)
        self.assertEqual(self.post(self.a, route, dict(body='x'*2001)).status_code, 400)

    def test_other_professional_cannot_access(self):
        self.record()
        with app.app_context():
            uid = db().execute("INSERT INTO users(name,email,password,role,created) VALUES('Outro','coaching-other@example.test','unused','admin',?)", (now(),)).lastrowid
            db().commit()
        client = app.test_client()
        with client.session_transaction() as session:
            session['uid'] = uid
        route = f"/workout-sessions/{self.history(self.a)[0]['id']}/messages"
        self.assertEqual(self.post(client, route, dict(body='Oi')).status_code, 404)
        self.assertEqual(client.get('/api/entries').json, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
