#!/usr/bin/env python3
"""Cierra la entrega: escribe guion.txt desde el spec, verifica videos y copy.txt, e imprime todo para pegarlo en el chat.

Uso: python3 entregar.py <carpeta-del-video>
Espera:  <carpeta>/fuente/spec.json, <carpeta>/fuente/meta.json, <carpeta>/video-completo.mp4, <carpeta>/clips/*.mp4
         y <carpeta>/copy.txt (lo escribe Claude siguiendo references/copy-seo.md).
Crea:    <carpeta>/guion.txt  (solo el texto de la voz, para teleprompter), portada.txt y portada.png (título para la portada)
"""
import json, os, re, subprocess, sys

folder = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
ok = True
def fail(msg):
    global ok; ok = False; print('✗', msg)
def good(msg): print('✓', msg)
def mmss(s): s = int(round(s)); return f'{s // 60:02d}:{s % 60:02d}'

spec = json.load(open(os.path.join(folder, 'fuente', 'spec.json')))
meta = json.load(open(os.path.join(folder, 'fuente', 'meta.json')))
slides = meta['slides']
total = meta['total']

# ---------------------------------------------------------------- guion.txt
# Solo el texto que dirá (para pegarlo en el teleprompter): sin título, tiempos, marcas de cara ni indicaciones de pantalla.
words = sum(m['palabras'] for m in slides)
def limpio(t): return re.sub(r'\s+', ' ', re.sub(r'\[[^\]]*\]', ' ', t)).strip()
guion = '\n\n'.join(limpio(sl['voz']) for sl in spec['escenas']) + '\n'
open(os.path.join(folder, 'guion.txt'), 'w').write(guion)
good(f'guion.txt escrito (solo texto, {words} palabras, ~{mmss(total)})')

# ---------------------------------------------------------------- portada (título + imagen para poner de portada)
# portada.txt = el título de portada (spec.portada, o el título de la primera escena); portada.png = imagen 1080x1920 de ese título.
def plano(t): return re.sub(r'[*~=]', '', str(t)).strip()
portada = plano(spec.get('portada') or slides and spec['escenas'][0].get('title', spec.get('titulo', '')))
open(os.path.join(folder, 'portada.txt'), 'w').write(portada.upper() + '\n')
good('portada.txt escrito')
html = os.path.join(folder, 'fuente', 'video.html')
sec = max(0.5, min(4.0, slides[0]['duration'] - 0.5))
tmp = os.path.join(folder, 'fuente', '_portada')
r = subprocess.run(['node', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'export_video.mjs'), html, tmp, '--still', f'1:{sec}'], capture_output=True, text=True)
png = os.path.join(tmp, 'still-1.png')
if r.returncode == 0 and os.path.exists(png):
    import shutil; shutil.copy(png, os.path.join(folder, 'portada.png')); shutil.rmtree(tmp, ignore_errors=True)
    good('portada.png generada (imagen del título, 1080x1920)')
else:
    fail('no se pudo generar portada.png: ' + (r.stderr or '')[:200])

# ---------------------------------------------------------------- videos
def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height:format=duration', '-of', 'json', path], capture_output=True, text=True)
    try:
        j = json.loads(r.stdout); return j['streams'][0]['width'], j['streams'][0]['height'], float(j['format']['duration'])
    except Exception:
        return None

full = os.path.join(folder, 'video-completo.mp4')
p = probe(full) if os.path.exists(full) else None
if not p: fail('falta video-completo.mp4 o no se puede leer')
else:
    w, h, d = p
    if (w, h) != (1080, 1920): fail(f'video-completo.mp4: tamaño {w}x{h} (debe ser 1080x1920)')
    elif abs(d - total) > 0.25: fail(f'video-completo.mp4 dura {d:.1f} s y el plan dice {total:.1f} s')
    else: good(f'video-completo.mp4: {w}x{h}, {d:.1f} s')
for m in slides:
    path = os.path.join(folder, 'clips', f"{m['index']:02d}-{m['id']}.mp4")
    p = probe(path) if os.path.exists(path) else None
    if not p: fail(f'falta el clip {os.path.basename(path)}'); continue
    w, h, d = p
    if (w, h) != (1080, 1920) or abs(d - m['duration']) > 0.25: fail(f'{os.path.basename(path)}: {w}x{h}, {d:.1f} s (esperaba 1080x1920, {m["duration"]:.1f} s)')
    else: good(f'clips/{os.path.basename(path)}: {d:.1f} s')

# ---------------------------------------------------------------- copy.txt
copy_path = os.path.join(folder, 'copy.txt')
copy = ''
if not os.path.exists(copy_path): fail('falta copy.txt')
else:
    copy = open(copy_path).read()
    lines = [l.strip() for l in copy.splitlines() if l.strip()]
    tag_lines = [l for l in lines if re.fullmatch(r'(#\w+\s*)+', l)]
    if len(tag_lines) != 1: fail(f'debe haber exactamente una línea de hashtags (hay {len(tag_lines)})')
    else:
        n = len(re.findall(r'#\w+', tag_lines[0]))
        good('5 hashtags') if n == 5 else fail(f'hay {n} hashtags (deben ser 5)')
        if lines[-1] != tag_lines[0]: fail('la línea de hashtags debe ser la última del copy')
    hook = lines[0] if lines else ''
    good(f'gancho de {len(hook)} caracteres') if len(hook) <= 125 else print(f'! el gancho tiene {len(hook)} caracteres (ideal ≤ 125)')
    if 'ígueme para más contenido tech' not in copy: fail('el copy no incluye el CTA "Sígueme para más contenido tech"')
    if len(copy) > 2200: fail(f'el copy pasa de 2.200 caracteres ({len(copy)})')
    kw = spec.get('palabra_clave', '').lower()
    if kw and kw not in hook.lower(): print(f'! la palabra clave "{kw}" no está en el gancho')

print('\n' + '=' * 60 + '\nCARPETA: ' + folder + '\n' + '=' * 60)
print('\nTÍTULO DE PORTADA (portada.txt / portada.png)\n  ' + portada.upper().replace('\n', '\n  '))
print('\nVIDEOS\n  video-completo.mp4  (' + mmss(total) + ')')
for m in slides: print(f"  clips/{m['index']:02d}-{m['id']}.mp4  ({m['duration']:.1f} s)")
print('\n' + '=' * 60 + '\nCOPY (copy.txt)\n' + '=' * 60 + '\n' + copy)
print('=' * 60 + '\nGUION (guion.txt)\n' + '=' * 60 + '\n' + guion)
print('\nTODO OK' if ok else '\nHAY PROBLEMAS')
sys.exit(0 if ok else 1)
