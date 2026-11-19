"""Perfis pessoais e compartilhamento opcional dentro dos rankings da equipe."""
import io
import secrets
import warnings
from flask import abort, jsonify, request, send_file
from PIL import Image, ImageOps, UnidentifiedImageError


def register(app, c):
    with app.app_context():
        c.db().execute('''CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            public_key TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL DEFAULT '',
            bio TEXT NOT NULL DEFAULT '',
            shared INTEGER NOT NULL DEFAULT 0,
            photo BLOB,
            revision INTEGER NOT NULL DEFAULT 0)''')
        c.db().commit()

    def own(uid):
        return c.one('SELECT public_key,display_name,bio,shared,photo IS NOT NULL AS has_photo,revision FROM user_profiles WHERE user_id=?', (uid,))

    def ensure(uid):
        c.db().execute('INSERT OR IGNORE INTO user_profiles(user_id,public_key) VALUES(?,?)', (uid, secrets.token_hex(24)))

    def payload(p):
        if not p:
            return dict(display_name='', bio='', shared=False, photo_url=None)
        return dict(display_name=p['display_name'], bio=p['bio'], shared=bool(p['shared']),
                    photo_url=f"/api/profiles/{p['public_key']}/photo?v={p['revision']}" if p['has_photo'] else None)

    def visible_profile(key):
        viewer = c.user()
        p = c.one('''SELECT p.*,u.role,u.status,u.professional_id FROM user_profiles p
            JOIN users u ON u.id=p.user_id WHERE p.public_key=?''', (key,))
        if not p:
            abort(404)
        if viewer['id'] != p['user_id']:
            abort(404)
        return p

    @app.get('/api/profile')
    def get_profile():
        return jsonify(payload(own(c.user()['id'])))

    @app.post('/api/profile')
    def save_profile():
        u = c.user()
        d = c.body()
        name = c.text(d, 'display_name', False, 40)
        bio = c.text(d, 'bio', False, 160)
        shared = d.get('shared', False)
        if type(shared) is not bool:
            abort(400)
        if shared:
            abort(400, description='Use a escolha de compartilhamento da jornada.')
        ensure(u['id'])
        c.db().execute('UPDATE user_profiles SET display_name=?,bio=?,shared=? WHERE user_id=?', (name, bio, int(shared), u['id']))
        c.db().execute('INSERT INTO privacy_events(actor,professional_id,action,version,created) VALUES(?,?,?,?,?)',
                       (u['id'], c.tenant(u), 'Perfil: compartilhamento autorizado' if shared else 'Perfil: compartilhamento desligado', 'profile-v1', c.now()))
        c.db().commit()
        return jsonify(payload(own(u['id'])))

    @app.post('/api/profile/photo')
    def upload_photo():
        u = c.user()
        file = request.files.get('file')
        if not file:
            abort(400, description='Selecione uma foto JPG, PNG ou WebP.')
        raw = file.read(5 * 1024 * 1024 + 1)
        if len(raw) > 5 * 1024 * 1024:
            abort(400, description='A foto deve ter até 5 MB.')
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(raw)) as source:
                    if source.format not in ('JPEG', 'PNG', 'WEBP') or source.width * source.height > 20_000_000:
                        raise ValueError()
                    source.load()
                    pic = ImageOps.exif_transpose(source).convert('RGB')
                    pic = ImageOps.fit(pic, (512, 512), method=Image.Resampling.LANCZOS)
                    # Re-encode without EXIF/location metadata or extra frames.
                    out = io.BytesIO()
                    pic.save(out, 'JPEG', quality=88)
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
            abort(400, description='Use uma foto válida JPG, PNG ou WebP de até 20 megapixels.')
        ensure(u['id'])
        c.db().execute('UPDATE user_profiles SET photo=?,revision=revision+1 WHERE user_id=?', (out.getvalue(), u['id']))
        c.db().commit()
        return jsonify(payload(own(u['id'])))

    @app.delete('/api/profile/photo')
    def remove_photo():
        u = c.user()
        c.db().execute('UPDATE user_profiles SET photo=NULL,revision=revision+1 WHERE user_id=?', (u['id'],))
        c.db().commit()
        return jsonify(payload(own(u['id'])))

    @app.get('/api/profiles/<key>')
    def public_profile(key):
        p = visible_profile(key)
        p['has_photo'] = p['photo'] is not None
        return jsonify(display_name=p['display_name'] or 'Participante', bio=p['bio'], photo_url=payload(p)['photo_url'], highlights=c.journey_highlights(p['user_id']))

    @app.get('/api/profiles/<key>/photo')
    def photo(key):
        p = visible_profile(key)
        if p['photo'] is None:
            abort(404)
        return send_file(io.BytesIO(p['photo']), mimetype='image/jpeg', conditional=False, etag=False)
