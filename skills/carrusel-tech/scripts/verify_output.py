#!/usr/bin/env python3
"""Verifica la carpeta entregable: un MP4 por slide (1080x1920, >=10 s) y copy.md con 5 hashtags al final.
Uso: python3 verify_output.py <carpeta>"""
import json, os, re, subprocess, sys

folder = sys.argv[1] if len(sys.argv) > 1 else '.'
ok = True
def fail(msg):
    global ok; ok = False; print('✗', msg)
def good(msg): print('✓', msg)

meta_path = os.path.join(folder, 'fuente', 'meta.json')
n_expected = len(json.load(open(meta_path))['slides']) if os.path.exists(meta_path) else None
videos = sorted(f for f in os.listdir(folder) if re.match(r'slide-\d+-.*\.mp4$', f))
if n_expected and len(videos) != n_expected: fail(f'hay {len(videos)} videos y el spec tiene {n_expected} slides')
elif not videos: fail('no hay videos')
for v in videos:
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,duration', '-of', 'csv=p=0', os.path.join(folder, v)], capture_output=True, text=True)
    try:
        w, h, d = r.stdout.strip().split(','); w, h, d = int(w), int(h), float(d)
    except Exception:
        fail(f'{v}: no se pudo leer'); continue
    if (w, h) != (1080, 1920): fail(f'{v}: tamaño {w}x{h} (debe ser 1080x1920)')
    elif d < 9.99: fail(f'{v}: dura {d:.1f} s (mínimo 10 s)')
    else: good(f'{v}: {w}x{h}, {d:.1f} s')

copy = os.path.join(folder, 'copy.md')
if not os.path.exists(copy): fail('falta copy.md')
else:
    text = open(copy).read()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    tags = re.findall(r'#\w+', ' '.join(l for l in lines if l.startswith('#') and not l.startswith('# ') and not l.startswith('## ')))
    # los hashtags son la línea de #palabras (no encabezados markdown)
    tag_lines = [l for l in lines if re.fullmatch(r'(#\w+\s*)+', l)]
    if len(tag_lines) != 1: fail(f'debe haber exactamente una línea de hashtags (hay {len(tag_lines)})')
    else:
        n = len(re.findall(r'#\w+', tag_lines[0]))
        good('5 hashtags') if n == 5 else fail(f'hay {n} hashtags (deben ser 5)')
    m = re.search(r'## Descripción\s*\n+(.+)', text)
    if m:
        hook = m.group(1).strip()
        good(f'gancho de {len(hook)} caracteres') if len(hook) <= 125 else print(f'! el gancho tiene {len(hook)} caracteres (ideal ≤ 125)')
    if 'ígueme para más contenido tech' not in text: fail('el copy no incluye el CTA "Sígueme para más contenido tech"')
    desc = text.split('## Texto alternativo')[0]
    if len(desc) > 2200: fail(f'la descripción pasa de 2.200 caracteres ({len(desc)})')
print('\nTODO OK' if ok else '\nHAY PROBLEMAS')
sys.exit(0 if ok else 1)
