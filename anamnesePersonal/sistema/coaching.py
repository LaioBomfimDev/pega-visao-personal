"""Conversa privada vinculada a cada sessão de treino registrada."""
from flask import abort, jsonify


def register(app, c):
    with app.app_context():
        c.db().execute('''CREATE TABLE IF NOT EXISTS workout_messages (
            id INTEGER PRIMARY KEY,
            log_id INTEGER NOT NULL REFERENCES activity_logs(id),
            author INTEGER NOT NULL REFERENCES users(id),
            body TEXT NOT NULL,
            created TEXT NOT NULL)''')
        c.db().execute('CREATE INDEX IF NOT EXISTS workout_messages_log ON workout_messages(log_id,id)')
        c.db().commit()

    @app.post('/api/workout-sessions/<int:log_id>/messages')
    def send_message(log_id):
        u = c.user()
        row = c.one('''SELECT l.*,e.professional_id FROM activity_logs l
            JOIN entries e ON e.id=l.entry_id WHERE l.id=? AND e.kind='workout' ''', (log_id,))
        if (not row or u['role'] == 'superadmin' or c.tenant(u) != row['professional_id']
                or u['role'] == 'student' and row['user_id'] != u['id']):
            abort(404, description='Sessão não encontrada.')
        message = c.text(c.body(), 'body', True, 2000)
        mid = c.insert('INSERT INTO workout_messages(log_id,author,body,created) VALUES(?,?,?,?)',
                       (log_id, u['id'], message, c.now()))
        recipient = row['user_id'] if u['role'] == 'admin' else row['professional_id']
        c.notify([recipient], u['name'] + ' enviou uma mensagem sobre seu treino', row['entry_id'])
        c.db().commit()
        return jsonify(id=mid), 201
