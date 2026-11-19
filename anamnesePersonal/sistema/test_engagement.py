import unittest
from datetime import date
from unittest.mock import patch
import test_app as base
from app import app, db


class EngagementTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base.SystemTest.setUpClass.__func__(cls)

    def setUp(self):
        with app.app_context():
            db().execute('DELETE FROM workout_messages')
            db().execute('DELETE FROM activity_logs')
            db().commit()
        self.student, _, self.uid = self.students[0]
        r = self.a.post('/api/entries', json=dict(kind='workout', target=self.uid, title='Treino', payload=dict(exercises=[dict(name='Remada', sets='3', reps='10', rest='60s')])), headers={'X-CSRF-Token': self.t})
        self.eid = r.json['id']

    def seed(self, stamps):
        with app.app_context():
            for stamp in stamps:
                db().execute('INSERT INTO activity_logs(entry_id,user_id,body,created) VALUES(?,?,?,?)', (self.eid, self.uid, '{}', stamp))
            db().commit()

    def summary(self, day):
        with patch('privacy.today', return_value=day):
            return self.student.get('/api/privacy').json['activity']

    def test_daily_streak_unique_dates_and_brasilia(self):
        self.seed(['2026-09-09T12:00:00+00:00','2026-09-10T12:00:00+00:00','2026-09-11T01:00:00+00:00'])
        a = self.summary(date(2026,9,11))
        self.assertEqual(a['daily_streak'], 2)
        self.assertEqual(a['total_days'], 2)
        self.assertFalse(a['trained_today'])
        self.assertEqual(len(a['week']), 7)
        self.assertEqual(a['week'][-1]['date'], '2026-09-11')
        self.assertEqual(sum(x['trained'] for x in a['week']), 2)
        self.seed(['2026-09-11T14:00:00+00:00'])
        self.assertEqual(self.summary(date(2026,9,11))['daily_streak'], 3)

    def test_gap_keeps_best_and_ignores_future(self):
        self.seed(['2026-09-01T12:00:00+00:00','2026-09-02T12:00:00+00:00','2026-09-03T12:00:00+00:00','2026-09-11T12:00:00+00:00','2026-09-20T12:00:00+00:00'])
        a=self.summary(date(2026,9,11))
        self.assertEqual((a['daily_streak'],a['best_streak'],a['total_days']), (1,3,4))
        self.assertEqual(self.summary(date(2026,9,13))['daily_streak'],0)

    def test_personal_summary_is_private_without_ranking_enrollment(self):
        self.seed(['2026-09-11T12:00:00+00:00'])
        self.assertEqual(self.summary(date(2026,9,11))['total_days'],1)
        self.assertEqual(self.students[1][0].get('/api/privacy').json['activity']['total_days'],0)
        self.assertEqual(self.students[1][0].get('/api/rankings').status_code,410)
        self.assertIsNone(self.a.get('/api/privacy').json['activity'])
        self.assertEqual(app.test_client().get('/api/privacy').status_code,401)


if __name__ == '__main__':
    unittest.main(verbosity=2)
