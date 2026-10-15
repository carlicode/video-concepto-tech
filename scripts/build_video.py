#!/usr/bin/env python3
"""Genera el video-explicación HTML (1080x1920, estilo tech negro+rosa+violeta) a partir de un spec JSON.
Cada escena dura lo que dura su texto de voz, y sus animaciones se reparten para terminar justo con la voz.

Uso:
  python3 build_video.py spec.json --out fuente            # compila video.html + meta.json
  python3 build_video.py spec.json --plan                  # solo valida y muestra tiempos (sin escribir nada)
  python3 build_video.py spec.json --out fuente --audio voz.m4a                 # ajusta la duración al audio real (reparte por palabras)
  python3 build_video.py spec.json --out fuente --cortes 9.8,24.1,41.0,58.5     # segundos EXACTOS donde termina cada escena (todas menos la última)
Los tipos de escena están en references/escenas.md.
"""
import argparse, json, math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine
from engine import SpecError, need, esc

ASSETS = os.path.join(HERE, '..', 'assets')
FPS = 30
HOLD = 1.0          # segundos con todo visible al final de la escena (la voz aún puede estar terminando)
MIN_SCENE = 3.5     # una escena no baja de esto
K_MIN, K_MAX = 0.55, 3.0   # límites del reescalado de animaciones


def words(s):
    return len(re.sub(r'\[[^\]]*\]', ' ', s or '').split())


def frames(sec):
    return max(1, round(sec * FPS))


def audio_len(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True)
    return float(r.stdout.strip())


def scale_times(html, k):
    """Multiplica todos los retardos de animación (--t, --f, --dur) por k."""
    return re.sub(r'--(t|f|dur):([0-9.]+)s', lambda m: f'--{m.group(1)}:{float(m.group(2)) * k:.2f}s', html)


def cues_of(html):
    return sorted({round(float(x), 1) for x in re.findall(r'--t:([0-9.]+)s', html)})


def build(spec_path, out_dir, audio=None, cortes=None, plan=False):
    spec = json.load(open(spec_path))
    scenes = need(spec, 'escenas', 'spec')
    if not 3 <= len(scenes) <= 12: raise SpecError(f'Usa entre 3 y 12 escenas (tienes {len(scenes)})')
    handle = spec.get('handle', '@carli.code')
    ritmo = float(spec.get('ritmo', 2.6))      # palabras por segundo al hablar
    pausa = float(spec.get('pausa', 0.5))

    # 1) duración de cada escena
    wc = [words(s.get('voz', '')) for s in scenes]
    if any(w == 0 for w in wc): raise SpecError('Todas las escenas necesitan "voz" (el texto que dirás)')
    if cortes:
        ends = [float(x) for x in cortes.split(',')]
        if len(ends) != len(scenes) - 1: raise SpecError(f'--cortes necesita {len(scenes)-1} valores (uno por escena menos la última)')
        total = audio_len(audio) if audio else None
        if total is None: raise SpecError('--cortes necesita también --audio (para saber dónde termina la última escena)')
        ends.append(total)
        durs = [ends[0]] + [ends[i] - ends[i - 1] for i in range(1, len(ends))]
    elif audio:
        total = audio_len(audio)
        durs = [total * w / sum(wc) for w in wc]
    else:
        durs = [max(MIN_SCENE, w / ritmo + pausa) for w in wc]
    for i, s in enumerate(scenes):
        if 'dur' in s: durs[i] = float(s['dur'])
    fr = [frames(d) for d in durs]
    durs = [f / FPS for f in fr]     # múltiplos exactos de 1/30 s

    # 2) HTML de cada escena, con las animaciones repartidas según su duración
    parts, meta, start = [], [], 0.0
    for i, sl in enumerate(scenes, 1):
        t = sl.get('type')
        if t not in engine.LAYOUTS: raise SpecError(f"Escena {i}: tipo '{t}' desconocido. Tipos: {sorted(engine.LAYOUTS)}")
        html, end = engine.LAYOUTS[t](sl, i)
        k, warn = 1.0, None
        if end > 0:
            k_raw = (durs[i - 1] - HOLD) / end
            k = min(K_MAX, max(K_MIN, k_raw))
            if k_raw < K_MIN: warn = f'va muy rápida (voz de {durs[i-1]:.1f}s para animación de {end:.1f}s): alarga la voz o quita elementos'
            elif k_raw > K_MAX: warn = f'va muy lenta (voz de {durs[i-1]:.1f}s para animación de {end:.1f}s): divide la escena o añade contenido'
            html = scale_times(html, k)
        parts.append(html.replace('{HANDLE}', esc(handle)))
        meta.append({'index': i, 'type': t, 'id': re.sub(r'[^a-z0-9-]+', '-', str(sl.get('id', t)).lower()).strip('-') or t,
                     'duration': round(durs[i - 1], 3), 'frames': fr[i - 1], 'start': round(start, 3),
                     'offset': 3 if (t == 'cover' and not sl.get('solo_titulo')) else 0, 'animation_end': round(end * k, 2), 'k': round(k, 2),
                     'palabras': wc[i - 1], 'cara': bool(sl.get('cara')), 'cues': cues_of(html), 'aviso': warn})
        start += durs[i - 1]

    if plan:
        print(f'{len(scenes)} escenas · {sum(wc)} palabras · {start:.1f} s en total ({start/60:.1f} min)')
        for m in meta:
            print(f"  {m['index']:>2}. {m['id']:<14} {m['type']:<10} {m['start']:6.1f} → {m['start']+m['duration']:6.1f} s  ({m['palabras']:>3} palabras)"
                  f"{'  CARA' if m['cara'] else ''}")
            print(f"      aparece a los: {', '.join(f'{c:g}' for c in m['cues']) or '—'} s (dentro de la escena)")
            if m['aviso']: print(f"      ! {m['aviso']}")
        return None, meta

    os.makedirs(out_dir, exist_ok=True)
    css = open(os.path.join(ASSETS, 'tech.css')).read()
    js = re.sub(r'const DUR=\[[^\]]*\];', 'const DUR=' + json.dumps([m['duration'] for m in meta]) + ';', open(os.path.join(ASSETS, 'tech.js')).read())
    title = esc(spec.get('titulo', 'Video'))
    page = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;500;700&family=Poppins:wght@800;900&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<div id="viewport"><div id="stage"><div class="bg"><div class="blob b1"></div><div class="blob b2"></div></div>{''.join(parts)}</div></div>
<div id="ui"><button id="prev">←</button><div id="dots"></div><button id="play">⏸ Pausa</button><button id="next">→</button><button id="loop">Reiniciar</button></div>
<script>{js}</script></body></html>'''
    html_path = os.path.join(out_dir, 'video.html')
    open(html_path, 'w').write(page)
    json.dump({'title': spec.get('titulo'), 'total': round(start, 3), 'slides': meta}, open(os.path.join(out_dir, 'meta.json'), 'w'), indent=2, ensure_ascii=False)
    return html_path, meta


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('spec'); ap.add_argument('--out'); ap.add_argument('--plan', action='store_true')
    ap.add_argument('--audio'); ap.add_argument('--cortes')
    a = ap.parse_args()
    if not a.plan and not a.out: ap.error('falta --out (o usa --plan)')
    try:
        path, meta = build(a.spec, a.out, a.audio, a.cortes, a.plan)
    except SpecError as e:
        print(f'ERROR de spec: {e}', file=sys.stderr); sys.exit(2)
    if path:
        print(path)
        for m in meta:
            print(f"  escena {m['index']} ({m['type']}, {m['id']}): {m['duration']:.1f} s" + (f"  ! {m['aviso']}" if m['aviso'] else ''))
        print(f"  total: {sum(m['duration'] for m in meta):.1f} s")
