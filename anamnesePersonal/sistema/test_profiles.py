import io
import unittest
import test_app as base
from app import app, db, now
from PIL import Image


class ProfileTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base.SystemTest.setUpClass.__func__(cls)

    def setUp(self):
        with app.app_context():
            for table in ('user_profiles', 'ranking_consent', 'ranking_settings', 'goal_members', 'goals'):
                db().execute('DELETE FROM ' + table)
            db().commit()
        self.owner, self.token, self.uid = self.students[0]
        self.peer = self.students[1][0]

    def save(self, shared=False, confirmed=False):
        return self.owner.post('/api/profile', json=dict(display_name='Foco', bio='Um treino por vez.', shared=shared, confirmed=confirmed), headers={'X-CSRF-Token': self.token})

    def post(self, client, path, data):
        token = client.get('/api/session').json['csrf']
        return client.post(path, json=data, headers={'X-CSRF-Token': token})

    def upload(self):
        data = io.BytesIO()
        exif = Image.Exif()
        exif[270] = 'Metadata privada'
        Image.new('RGB', (90, 60), 'orange').save(data, 'JPEG', exif=exif)
        data.seek(0)
        r = self.owner.post('/api/profile/photo', data={'file': (data, 'perfil.jpg')}, headers={'X-CSRF-Token': self.token})
        self.assertEqual(r.status_code, 200, r.json)
        return r.json['photo_url']

    def enable(self):
        self.assertEqual(self.post(self.a, '/api/privacy/settings', dict(enabled=True, confirmed=True)).status_code, 200)

    def participate(self):
        self.assertEqual(self.post(self.owner, '/api/privacy/consent', dict(alias='Atleta Foco', attendance=True, confirmed=True)).status_code, 200)

    def test_private_default_and_validated_upload(self):
        self.assertFalse(self.owner.get('/api/profile').json['shared'])
        url = self.upload()
        response = self.owner.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        image = Image.open(io.BytesIO(response.data))
        self.assertEqual(image.size, (512, 512))
        self.assertEqual(dict(image.getexif()), {})
        self.assertEqual(self.peer.get(url).status_code, 404)
        self.assertEqual(self.a.get(url).status_code, 404)
        self.assertEqual(app.test_client().get(url).status_code, 401)
        r = self.owner.post('/api/profile/photo', data={'file': (io.BytesIO(b'<svg/>'), 'evil.svg')}, headers={'X-CSRF-Token': self.token})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.owner.get(url).status_code, 200)





    def test_invalid_fields_and_csrf(self):
        self.assertEqual(self.owner.post('/api/profile', json={}).status_code, 403)
        self.assertEqual(self.post(self.owner, '/api/profile', dict(shared='yes')).status_code, 400)
        self.assertEqual(self.post(self.owner, '/api/profile', dict(bio='x'*161)).status_code, 400)
        self.assertEqual(self.post(self.a, '/api/profile', dict(shared=True, confirmed=True)).status_code, 400)


if __name__ == '__main__':
    unittest.main(verbosity=2)
