"""Personal milestones and explicitly selected highlights, visible within one team."""
import io
import json
import secrets
from datetime import datetime
from flask import abort, jsonify, send_file
from privacy import BRASILIA, today

MILESTONES = [
    dict(id='first', title='Dei meu primeiro passo', symbol='🌱', description='Registrei meu primeiro treino.'),
    dict(id='rhythm', title='Encontrando meu ritmo', symbol='🌿', description='Estou construindo espaço para me cuidar.'),
    dict(id='story', title='Construindo minha história', symbol='🍃', description='Cada passo faz parte da minha jornada.'),
    dict(id='month', title='Um mês de acompanhamento', symbol='🌼', description='Minha história de acompanhamento começou há um mês ou mais.'),
    dict(id='return', title='Retomei meus registros', symbol='☀️', description='Recomeçar também faz parte da minha jornada.'),
]


def register(app, c):
    with app.app_context():
        c.db().execute('''CREATE TABLE IF NOT EXISTS journey_sharing (
            user_id INTEGER PRIMARY KEY REFERENCES users(id), public_key TEXT UNIQUE NOT NULL,
            shared INTEGER NOT NULL DEFAULT 0, selected TEXT NOT NULL DEFAULT '[]')''')
        c.db().commit()

    def member():
        u = c.user()
        if u['role'] == 'superadmin':
            abort(403)
        return u

    def earned(uid):
        days = set()
        for row in c.rows('''SELECT l.created FROM activity_logs l JOIN entries e ON e.id=l.entry_id
                JOIN users u ON u.id=l.user_id WHERE l.user_id=? AND e.kind='workout'
                AND e.professional_id=u.professional_id''', (uid,)):
            day = datetime.fromisoformat(row['created']).astimezone(BRASILIA).date()
            if day <= today():
                days.add(day)
        ordered = sorted(days)
        user = c.one('SELECT created FROM users WHERE id=?', (uid,))
        joined = datetime.fromisoformat(user['created']).astimezone(BRASILIA).date()
        ids = set()
        if ordered:
            ids.add('first')
            if len(days) >= 5:
                ids.add('rhythm')
            if len(days) >= 10:
                ids.add('story')
            if (today() - joined).days >= 30:
                ids.add('month')
            if any((b - a).days >= 7 for a, b in zip(ordered, ordered[1:])):
                ids.add('return')
        return [m.copy() for m in MILESTONES if m['id'] in ids]

    def settings(uid):
        return c.one('SELECT * FROM journey_sharing WHERE user_id=?', (uid,)) or dict(shared=0, selected='[]')

    def highlights(uid):
        config = settings(uid)
        if not config['shared']:
            return []
        by_id = {m['id']: m for m in earned(uid)}
        return [by_id[mid] for mid in json.loads(config['selected']) if mid in by_id][:3]

    c.journey_highlights = highlights

    def profile(key):
        viewer = member()
        p = c.one('''SELECT j.*,u.professional_id,u.status,u.role,p.display_name,p.bio,p.photo,p.revision
                FROM journey_sharing j JOIN users u ON u.id=j.user_id
                LEFT JOIN user_profiles p ON p.user_id=j.user_id WHERE j.public_key=?''', (key,))
        if (not p or not p['shared'] or p['status'] != 'active' or p['role'] != 'student'
                or c.tenant(viewer) != p['professional_id']):
            abort(404)
        return p

    def public_payload(p):
        return dict(key=p['public_key'], display_name=p['display_name'] or 'Participante', bio=p['bio'] or '',
                    photo_url=f"/api/journey/profiles/{p['public_key']}/photo?v={p['revision']}" if p['photo'] else None,
                    highlights=highlights(p['user_id']))

    @app.get('/api/journey')
    def own_journey():
        u = member()
        config = settings(u['id'])
        return jsonify(earned=earned(u['id']) if u['role'] == 'student' else [],
                       shared=bool(config['shared']), selected=json.loads(config['selected']))

    @app.post('/api/journey')
    def save_journey():
        u, d = member(), c.body()
        if u['role'] != 'student':
            abort(403)
        selected, shared = d.get('selected', []), d.get('shared', False)
        if (type(shared) is not bool or not isinstance(selected, list) or len(selected) > 3
                or any(not isinstance(x, str) for x in selected) or len(set(selected)) != len(selected)):
            abort(400, description='Escolha até três marcos diferentes.')
        allowed = {m['id'] for m in earned(u['id'])}
        if not set(selected) <= allowed:
            abort(400, description='Escolha marcos que já fazem parte da sua jornada.')
        if shared and (d.get('confirmed') is not True or not selected):
            abort(400, description='Escolha os marcos e confirme o compartilhamento com a equipe.')
        c.db().execute('''INSERT INTO journey_sharing(user_id,public_key,shared,selected) VALUES(?,?,?,?)
                ON CONFLICT(user_id) DO UPDATE SET shared=excluded.shared,selected=excluded.selected''',
                       (u['id'], secrets.token_hex(24), int(shared), json.dumps(selected)))
        c.db().execute('INSERT INTO privacy_events(actor,professional_id,action,version,created) VALUES(?,?,?,?,?)',
                       (u['id'], c.tenant(u), 'Jornada: compartilhamento autorizado' if shared else 'Jornada: compartilhamento desligado', 'journey-v1', c.now()))
        c.db().commit()
        return jsonify(ok=True)

    @app.get('/api/journey/team')
    def team():
        u = member()
        rows = c.rows('''SELECT j.public_key FROM journey_sharing j JOIN users u ON u.id=j.user_id
                LEFT JOIN user_profiles p ON p.user_id=u.id
                WHERE j.shared=1 AND u.status='active' AND u.role='student' AND u.professional_id=?
                ORDER BY COALESCE(NULLIF(p.display_name,''),'Participante') COLLATE NOCASE,j.public_key''', (c.tenant(u),))
        return jsonify([public_payload(profile(row['public_key'])) for row in rows])

    @app.get('/api/journey/profiles/<key>')
    def shared_profile(key):
        return jsonify(public_payload(profile(key)))

    @app.get('/api/journey/profiles/<key>/photo')
    def shared_photo(key):
        p = profile(key)
        if not p['photo']:
            abort(404)
        return send_file(io.BytesIO(p['photo']), mimetype='image/jpeg', conditional=False, etag=False)
