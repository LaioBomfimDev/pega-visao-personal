"""Validated workout plans, repeated evaluations and coach-only notes."""
import json
import math
import re
import secrets
from datetime import date, datetime, timezone, timedelta
from flask import abort, jsonify


def clean(value, label, limit=180, required=False):
    if not isinstance(value, str) or len(value) > limit:
        abort(400, description='Confira ' + label + '.')
    value = value.strip()
    if required and not value:
        abort(400, description='Preencha ' + label + '.')
    return value


def workout_days(payload):
    return payload.get('days') or [{'id': 'legacy', 'title': 'Treino A',
                                   'weekdays': [], 'exercises': payload.get('exercises', [])}]


def normalize_workout(payload, version=1):
    if not isinstance(payload, dict):
        abort(400)
    days = payload.get('days')
    if days is None:
        days = workout_days(payload)
    if not isinstance(days, list) or not 1 <= len(days) <= 8:
        abort(400, description='Inclua de 1 a 8 dias na ficha.')
    result, identifiers, total = [], set(), 0
    for day in days:
        if not isinstance(day, dict):
            abort(400)
        identifier = day.get('id') or secrets.token_hex(8)
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', identifier) or identifier in identifiers:
            abort(400, description='Identificador de dia inválido ou repetido.')
        identifiers.add(identifier)
        weekdays = day.get('weekdays', [])
        if not isinstance(weekdays, list) or any(type(n) is not int or n not in range(7) for n in weekdays):
            abort(400, description='Confira os dias da semana.')
        exercises = day.get('exercises')
        if not isinstance(exercises, list) or not 1 <= len(exercises) <= 40:
            abort(400, description='Cada dia precisa de 1 a 40 exercícios.')
        normalized = []
        for exercise in exercises:
            if not isinstance(exercise, dict):
                abort(400)
            normalized.append({key: clean(exercise.get(key, ''), 'o exercício', 500 if key == 'notes' else 180, key == 'name')
                               for key in ('name', 'sets', 'reps', 'rest', 'notes')})
        total += len(normalized)
        result.append({'id': identifier, 'title': clean(day.get('title', ''), 'o nome do dia', 100, True),
                       'weekdays': sorted(set(weekdays)), 'exercises': normalized})
    if total > 160:
        abort(400, description='Limite de 160 exercícios por ficha.')
    if type(payload.get('active', True)) is not bool:
        abort(400)
    return {'version': version, 'active': payload.get('active', True), 'days': result,
            'exercises': [x for day in result for x in day['exercises']]}


def session_record(entry, record):
    payload = json.loads(entry['payload'])
    if payload.get('active', True) is False:
        abort(409, description='Esta ficha está arquivada. Consulte o planejamento atual.')
    version = payload.get('version', 1)
    if (version > 1 and 'plan_version' not in record) or record.get('plan_version', version) != version:
        abort(409, description='A ficha foi atualizada. Reabra o treino antes de registrar a sessão.')
    days = workout_days(payload)
    day_id = record.get('day_id', days[0]['id'] if len(days) == 1 else None)
    day = next((d for d in days if d['id'] == day_id), None)
    if not day:
        abort(400, description='Selecione um dia da ficha.')
    logs = record.get('logs')
    if not isinstance(logs, list) or len(logs) != len(day['exercises']):
        abort(400, description='Confira os exercícios realizados.')
    normalized = []
    for item, planned in zip(logs, day['exercises']):
        if not isinstance(item, dict) or type(item.get('done')) is not bool:
            abort(400)
        weight = item.get('weight', '')
        if weight not in ('', None):
            try:
                if isinstance(weight, bool) or not math.isfinite(float(weight)) or not 0 <= float(weight) <= 1000:
                    raise ValueError()
            except (ValueError, TypeError):
                abort(400, description='Confira as cargas.')
        normalized.append({**planned, 'weight': weight, 'done': item['done']})
    if not any(x['done'] for x in normalized):
        abort(400, description='Marque ao menos um exercício realizado.')
    feeling = record.get('feeling', '')
    if feeling not in ('', 'leve', 'na-medida', 'puxado', 'desconforto'):
        abort(400)
    rpe = record.get('rpe')
    if rpe is not None and (type(rpe) is not int or not 1 <= rpe <= 10):
        abort(400, description='Informe esforço de 1 a 10.')
    mood = record.get('mood', '')
    if mood not in ('', 'bem', 'normal', 'cansado'):
        abort(400)
    pain = record.get('pain', False)
    if type(pain) is not bool:
        abort(400)
    return {'logs': normalized, 'note': clean(record.get('note', ''), 'o relato', 1600), 'feeling': feeling,
            'rpe': rpe, 'mood': mood, 'pain': pain,
            'pain_details': clean(record.get('pain_details', ''), 'o desconforto', 500) if pain else '',
            'plan_version': version, 'plan_title': entry['title'], 'day_id': day_id, 'day_title': day['title'],
            'plan_snapshot': {'title': entry['title'], 'body': entry['body'], 'day': day, 'version': version}}


MEASURES = [
    ('weight', 'Peso (kg)', 1, 500), ('waist', 'Cintura (cm)', 1, 400),
    ('arm', 'Braço (cm)', 1, 200), ('hip', 'Quadril (cm)', 1, 400),
    ('thigh', 'Coxa (cm)', 1, 200), ('fat', 'Gordura corporal (%)', 0, 100),
    ('muscle', 'Massa muscular (kg)', 0, 300), ('pain_score', 'Dor percebida (0 a 10)', 0, 10)]
TEMPLATES = [
    {'id': 'monthly', 'title': 'Avaliação periódica', 'description': 'Medidas e percepção de evolução. Preencha apenas o que foi medido.',
     'fields': [{'id': k, 'label': label, 'type': 'number', 'min': lo, 'max': hi} for k, label, lo, hi in MEASURES]},
    {'id': 'wellbeing', 'title': 'Rotina e bem-estar', 'description': 'Um retrato do seu sono, disposição e rotina de treinos.',
     'fields': [{'id': 'sleep', 'label': 'Horas de sono por noite', 'type': 'number', 'min': 0, 'max': 24},
                {'id': 'energy', 'label': 'Disposição (1 a 10)', 'type': 'number', 'min': 1, 'max': 10},
                {'id': 'stress', 'label': 'Estresse percebido (0 a 10)', 'type': 'number', 'min': 0, 'max': 10},
                {'id': 'training_days', 'label': 'Dias de treino na semana (0 a 7)', 'type': 'number', 'min': 0, 'max': 7}]},
    {'id': 'nutrition', 'title': 'Hábitos alimentares', 'description': 'Registre sua rotina para conversar com o profissional.',
     'fields': [{'id': 'water', 'label': 'Água por dia (litros)', 'type': 'number', 'min': 0, 'max': 15},
                {'id': 'meals', 'label': 'Refeições por dia', 'type': 'number', 'min': 1, 'max': 15},
                {'id': 'restrictions', 'label': 'Restrições e preferências', 'type': 'text'},
                {'id': 'routine', 'label': 'Rotina e dificuldades com a alimentação', 'type': 'text'}]}
]


def register(app, c):
    with app.app_context():
        c.db().executescript('''CREATE TABLE IF NOT EXISTS coach_notes (
            id INTEGER PRIMARY KEY, professional_id INTEGER NOT NULL REFERENCES users(id),
            student_id INTEGER NOT NULL REFERENCES users(id), body TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1, created TEXT NOT NULL, updated TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS coach_note_revisions (
            id INTEGER PRIMARY KEY, note_id INTEGER NOT NULL REFERENCES coach_notes(id),
            body TEXT NOT NULL, version INTEGER NOT NULL, created TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS coach_notes_student ON coach_notes(professional_id,student_id);''')
        c.db().commit()

    def own_student(uid):
        u = c.admin()
        if type(uid) is not int:
            abort(400, description='Selecione um aluno válido.')
        if not c.one("SELECT id FROM users WHERE id=? AND role='student' AND professional_id=?", (uid, u['id'])):
            abort(404)
        return u

    @app.get('/api/evaluation-templates')
    def templates():
        if c.user()['role'] == 'superadmin':
            abort(403)
        return jsonify(TEMPLATES)

    @app.post('/api/evaluations')
    def evaluation():
        u, d = c.user(), c.body()
        if u['role'] == 'superadmin':
            abort(403)
        target = u['id'] if u['role'] == 'student' else d.get('target')
        if u['role'] == 'admin':
            own_student(target)
        template = next((t for t in TEMPLATES if t['id'] == d.get('template_id')), None)
        if not template:
            abort(400)
        try:
            measured = date.fromisoformat(d.get('measured_at', ''))
            if measured > datetime.now(timezone(timedelta(hours=-3))).date() or measured.year < 1900:
                raise ValueError()
        except (TypeError, ValueError):
            abort(400, description='Informe uma data válida, até hoje.')
        values = d.get('values', {})
        if not isinstance(values, dict):
            abort(400)
        payload = {'template_id': template['id'], 'template_title': template['title'], 'measured_at': measured.isoformat(),
                   'period': measured.strftime('%Y-%m')}
        details = []
        for f in template['fields']:
            v = values.get(f['id'])
            if v in (None, ''):
                continue
            if f['type'] == 'number':
                try:
                    if isinstance(v, bool):
                        raise ValueError()
                    v = float(v)
                    if not math.isfinite(v) or not f['min'] <= v <= f['max']:
                        raise ValueError()
                except (TypeError, ValueError):
                    abort(400, description='Confira ' + f['label'] + '.')
            else:
                v = clean(v, f['label'], 1500)
                if not v:
                    continue
            payload[f['id']] = v
            details.append({'label': f['label'], 'value': str(v)})
        if not details:
            abort(400, description='Preencha pelo menos um campo da avaliação.')
        payload['sections'] = [{'title': template['title'], 'rows': details}]
        content = c.text(d, 'body', False, 4000)
        eid = c.insert('INSERT INTO entries(kind,author,target,audience,title,body,payload,created,professional_id) VALUES(?,?,?,\'private\',?,?,?,?,?)',
                       ('progress', u['id'], target, template['title'] + ' · ' + measured.strftime('%d/%m/%Y'), content,
                        json.dumps(payload, ensure_ascii=False), c.now(), c.tenant(u)))
        c.notify([target if u['role'] == 'admin' else c.tenant(u)], 'Nova avaliação: ' + u['name'], eid)
        c.db().commit()
        return jsonify(id=eid), 201

    @app.get('/api/students/<int:uid>/notes')
    def notes(uid):
        u = own_student(uid)
        return jsonify(c.rows('SELECT id,body,version,created,updated FROM coach_notes WHERE professional_id=? AND student_id=? ORDER BY id DESC', (u['id'], uid)))

    @app.post('/api/students/<int:uid>/notes')
    def add_note(uid):
        u = own_student(uid)
        content = c.text(c.body(), 'body', True, 5000)
        nid = c.insert('INSERT INTO coach_notes(professional_id,student_id,body,created,updated) VALUES(?,?,?,?,?)',
                       (u['id'], uid, content, c.now(), c.now()))
        c.db().commit()
        return jsonify(id=nid), 201

    @app.post('/api/students/<int:uid>/notes/<int:nid>')
    def edit_note(uid, nid):
        u, d = own_student(uid), c.body()
        content = c.text(d, 'body', True, 5000)
        c.db().execute('BEGIN IMMEDIATE')
        note = c.one('SELECT * FROM coach_notes WHERE id=? AND professional_id=? AND student_id=?', (nid, u['id'], uid))
        if not note:
            abort(404)
        if d.get('version') != note['version']:
            abort(409, description='A nota mudou. Reabra as notas antes de editar.')
        c.insert('INSERT INTO coach_note_revisions(note_id,body,version,created) VALUES(?,?,?,?)', (nid, note['body'], note['version'], c.now()))
        c.db().execute('UPDATE coach_notes SET body=?,version=version+1,updated=? WHERE id=?', (content, c.now(), nid))
        c.db().commit()
        return jsonify(ok=True)

    @app.get('/api/entries/<int:eid>/versions')
    def versions(eid):
        e = c.entry(eid, c.admin())
        if e['kind'] != 'workout':
            abort(400)
        previous = []
        for r in c.rows('SELECT snapshot,created FROM revisions WHERE entry_id=? ORDER BY id DESC', (eid,)):
            snapshot = json.loads(r['snapshot'])
            snapshot['payload'] = json.loads(snapshot['payload'])
            previous.append({'title': snapshot['title'], 'body': snapshot['body'], 'payload': snapshot['payload'], 'saved_at': r['created']})
        return jsonify(previous)
