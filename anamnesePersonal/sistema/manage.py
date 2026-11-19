from pathlib import Path
from contextlib import closing
import argparse, getpass, os, sqlite3, tempfile, zipfile
from datetime import datetime
from werkzeug.security import generate_password_hash
DATA=Path(os.getenv('ABEL_DATA_DIR',str(Path.home()/'AppData/Local/AbelAcompanhamento')))
p=argparse.ArgumentParser(description='Manutenção local do Abel Acompanhamento')
p.add_argument('command',choices=['backup','reset-password']);p.add_argument('email',nargs='?');a=p.parse_args()
if not (DATA/'abel.sqlite').exists():raise SystemExit('Abra o sistema primeiro.')
if a.command=='backup':
 (DATA/'backups').mkdir(exist_ok=True)
 output=DATA/'backups'/('abel-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.zip')
 with tempfile.TemporaryDirectory() as tmp:
  snapshot=Path(tmp)/'abel.sqlite'
  with closing(sqlite3.connect(DATA/'abel.sqlite')) as src, closing(sqlite3.connect(snapshot)) as dst:src.backup(dst)
  with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
   z.write(snapshot,'abel.sqlite')
   if (DATA/'session.key').exists():z.write(DATA/'session.key','session.key')
   for f in (DATA/'media').glob('*'):
    if f.is_file():z.write(f,'media/'+f.name)
 print('Backup criado:',output)
else:
 if not a.email:raise SystemExit('Informe o e-mail da conta.')
 password=getpass.getpass('Nova senha (10 ou mais caracteres): ')
 if len(password)<10:raise SystemExit('Senha muito curta.')
 if password!=getpass.getpass('Repita a senha: '):raise SystemExit('As senhas são diferentes.')
 with sqlite3.connect(DATA/'abel.sqlite') as conn:
  cur=conn.execute('UPDATE users SET password=?,session_version=session_version+1 WHERE email=?',(generate_password_hash(password),a.email.strip().lower()))
  if cur.rowcount!=1:raise SystemExit('Conta não encontrada.')
 print('Senha alterada.')
