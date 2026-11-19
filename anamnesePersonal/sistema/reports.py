"""Private PDF and DOCX downloads built from the authorized entry."""
import io
import json
from html import escape
from flask import abort, send_file
from planning import workout_days


def document_lines(entry, student, professional):
    payload = json.loads(entry['payload'])
    lines = [('title', entry['title']), ('text', 'Pega Visão Personal | Acompanhamento'),
             ('text', 'Aluno: ' + student), ('text', 'Profissional: ' + professional)]
    if entry['kind'] == 'workout':
        lines.append(('text', 'Versão ' + str(payload.get('version', 1)) + (' | Arquivada' if payload.get('active') is False else ' | Ativa')))
    if payload.get('measured_at'):
        lines.append(('text', 'Data da avaliação: ' + '/'.join(reversed(payload['measured_at'].split('-')))))
    if entry['body']:
        lines.append(('text', entry['body']))
    if entry['kind'] == 'workout':
        weekdays = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        for day in workout_days(payload):
            lines.append(('heading', day['title']))
            lines.append(('text', 'Dias: ' + (', '.join(weekdays[n] for n in day.get('weekdays', [])) or 'A combinar com o profissional')))
            for i, exercise in enumerate(day['exercises'], 1):
                lines.append(('heading', f"{i}. {exercise['name']}"))
                lines.append(('text', f"Séries: {exercise.get('sets', '')} | Repetições: {exercise.get('reps', '')} | Descanso: {exercise.get('rest', '')}"))
                if exercise.get('notes'):
                    lines.append(('text', exercise['notes']))
    elif payload.get('sections'):
        for section in payload['sections']:
            lines.append(('heading', section['title']))
            for row in section['rows']:
                lines.append(('text', row['label'] + ': ' + row['value']))
    else:
        for key, label in [('weight', 'Peso (kg)'), ('waist', 'Cintura (cm)'), ('energy', 'Disposição'), ('difficulty', 'Dificuldade')]:
            if payload.get(key) not in ('', None):
                lines.append(('text', label + ': ' + str(payload[key])))
    lines.append(('text', 'Documento individual. Compartilhe apenas com quem deve receber estas informações.'))
    # Keep valid XML characters for both Word and ReportLab's paragraph parser.
    return [(kind, ''.join(ch for ch in text if ch in '\n\t\r' or 32 <= ord(ch) <= 0xD7FF or 0xE000 <= ord(ch) <= 0xFFFD or 0x10000 <= ord(ch) <= 0x10FFFF)) for kind, text in lines]


def make_pdf(lines):
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    styles['Title'].textColor = colors.HexColor('#bd4c14')
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 15
    content = []
    for kind, text in lines:
        style = styles[{'title': 'Title', 'heading': 'Heading2', 'text': 'BodyText'}[kind]]
        content.extend([Paragraph(escape(text).replace('\n', '<br/>'), style), Spacer(1, 7)])
    def footer(canvas, doc):
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawString(42, 25, 'Pega Visão Personal | Acompanhamento individual')
        canvas.drawRightString(A4[0] - 42, 25, str(doc.page))
    SimpleDocTemplate(buffer, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=46,
                      title=lines[0][1], author='Pega Visão Personal').build(content, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    return buffer


def make_docx(lines):
    from docx import Document
    from docx.shared import Pt, RGBColor
    doc = Document()
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(11)
    doc.styles['Title'].font.color.rgb = RGBColor.from_string('BD4C14')
    for kind, text in lines:
        if kind == 'title':
            doc.add_heading(text, 0)
        elif kind == 'heading':
            doc.add_heading(text, 2)
        else:
            doc.add_paragraph(text)
    doc.sections[0].footer.paragraphs[0].text = 'Pega Visão Personal | Acompanhamento individual'
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def register(app, c):
    @app.get('/api/entries/<int:eid>/report.<fmt>')
    def report(eid, fmt):
        e = c.entry(eid, c.user())
        if fmt not in ('pdf', 'docx') or e['kind'] not in ('workout', 'assessment', 'progress', 'checkin'):
            abort(404)
        student = c.one('SELECT name FROM users WHERE id=?', (e['target'],))
        professional = c.one('SELECT name FROM users WHERE id=?', (e['professional_id'],))
        lines = document_lines(e, (student or {}).get('name', 'Aluno'), (professional or {}).get('name', 'Profissional'))
        if fmt == 'pdf':
            data, mime = make_pdf(lines), 'application/pdf'
        else:
            data, mime = make_docx(lines), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        return send_file(data, mimetype=mime, as_attachment=True, download_name=f'pegavisao-registro-{eid}.{fmt}')
