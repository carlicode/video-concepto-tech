#!/usr/bin/env python3
"""Genera un carrusel HTML vertical (1080x1920, estilo tech negro+rosa+violeta) a partir de un spec JSON.

Uso: python3 build_carousel.py spec.json [--out carpeta]
Salida: <out>/carousel.html  y  <out>/meta.json (duración y desfase de cada slide, usados por export_videos.mjs)
Los tipos de slide y sus campos están documentados en references/layouts.md.
"""
import json, math, os, re, sys, difflib
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, '..', 'assets')
PINK, VIO, BG, PANEL, LINE, INK, MUTE = '#ff4d94', '#a78bfa', '#09090b', '#111114', '#26262c', '#f4f4f5', '#8b8b95'
GRAY, DIMVIO = '#6b6b76', '#4a4468'
MIN_SECONDS = 10      # mínimo por slide (pedido del usuario)
HOLD = 3              # segundos con todo visible al final de cada slide


class SpecError(Exception):
    pass


# ----------------------------------------------------------------- utilidades
def rgb(h): return ','.join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))
def rgba(h, a): return f'rgba({rgb(h)},{a})'
def esc(s): return escape(str(s), quote=False)

def rich(s):
    """Texto de títulos: *palabra* -> rosa, \\n -> salto de línea."""
    s = esc(s)
    s = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', s)
    return s.replace('\n', '<br>')

def _icon_raw(name):
    path = os.path.join(ASSETS, 'icons', f'{name}.svg')
    if not os.path.exists(path):
        have = [f[:-4] for f in os.listdir(os.path.join(ASSETS, 'icons'))]
        near = difflib.get_close_matches(name, have, n=5)
        raise SpecError(f"Icono '{name}' no existe. Parecidos: {near}. Lista completa: ls assets/icons")
    return re.sub(r'<!--.*?-->', '', open(path).read(), flags=re.S)

def icon_inner(name):
    s = re.sub(r'^.*?<svg[^>]*>', '', _icon_raw(name), flags=re.S).replace('</svg>', '')
    return re.sub(r'\s+', ' ', s).strip()

def icon_html(name):
    s = re.sub(r'<svg[^>]*>', lambda x: re.sub(r'\s+(width|height|class)="[^"]*"', '', x.group(0)), _icon_raw(name), count=1)
    return re.sub(r'\s+', ' ', s).strip()

def gi(name, x, y, size, color, sw=1.8):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({size/24:.4f})" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{icon_inner(name)}</g>')

def text(x, y, s, size=28, weight=600, fill=INK, anchor='start', mono=False, extra=''):
    c = ' class="m"' if mono else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{c} {extra}>{esc(s)}</text>'

def G(c, t, cls='g'): return f'<g class="{cls}" style="--t:{t:.2f}s">{c}</g>'
def svgwrap(parts): return f'<div class="viz"><svg viewBox="0 0 912 1000">{"".join(parts)}</svg></div>'

def need(d, key, where):
    if key not in d:
        raise SpecError(f"Falta '{key}' en {where}")
    return d[key]


RAYS_L = ('<svg class="rays rl" width="96" height="96" viewBox="0 0 96 96" fill="none" stroke="#ff4d94" stroke-width="9" stroke-linecap="round">'
          '<path d="M10 62 38 54M16 30 40 40M40 8 48 34"/></svg>')
RAYS_R = ('<svg class="rays rr" width="96" height="96" viewBox="0 0 96 96" fill="none" stroke="#ffd60a" stroke-width="9" stroke-linecap="round">'
          '<path d="M86 34 58 42M80 66 56 56M56 88 48 62"/></svg>')

def title_html(s, tag='h2', pill=None, step=0.17, size=None):
    """Título que aparece palabra por palabra. *rosa*  ~amarillo~  \\n = salto de línea. Opcional: pastilla amarilla (pill)."""
    lines, n = [], 0
    for line in str(s).split('\n'):
        out = ''
        for m in re.finditer(r'(\s*)(==[^=]+==|\*[^*]+\*|~[^~]+~|[^\s*~=]+)', line):
            sp, tok = m.group(1), m.group(2)
            cls = 'pk' if tok[0] == '*' else 'yl' if tok[0] == '~' else 'mk' if tok[0] == '=' else ''
            ws = tok.strip('*~=').split()
            for j, w in enumerate(ws):
                gap = ' ' if (out and (sp or j > 0)) else ''
                out += gap + f'<span class="w {cls}" style="--w:{0.1 + n * step:.2f}s">{esc(w)}</span>'; n += 1
        lines.append(out)
    t_end = 0.1 + n * step + 0.25
    pill_html = f'<div class="pill" style="--w:{t_end:.2f}s">{esc(pill)}</div>' if pill else ''
    return (f'<div class="tw">{RAYS_L}{RAYS_R}<{tag} class="tt"{f' style="font-size:{size}px"' if size else ''}>{"<br>".join(lines)}</{tag}>{pill_html}</div>')


def frame(sl, body, idx):
    kicker = esc(sl.get('kicker', ''))          # opcional: en videos narrados se omite
    kick = f'<div class="kicker">// {kicker}</div>' if kicker else ''
    foot = '' if sl.get('sin_handle') else '<div class="foot">{HANDLE}</div>'
    head = title_html(need(sl, 'title', f'slide {idx}'), 'h2', sl.get('pill'), size=sl.get('title_px'))
    return f'''
<section class="slide">
  {kick}
  {head}
  {body}
  {foot}
</section>'''


LOGO = (f'<svg viewBox="0 0 64 64" fill="none"><rect width="64" height="64" rx="18" fill="{PINK}"/>'
        f'<path d="M40.4 23.2A14 14 0 1 0 40.4 40.8" stroke="{BG}" stroke-width="6" stroke-linecap="round"/>'
        f'<rect class="cur" x="43" y="40" width="11" height="5" rx="2.5" fill="{BG}"/></svg>')


# ----------------------------------------------------------------- layouts
# Cada layout devuelve (html, fin) donde fin = segundo en que termina su última animación.

def L_cover(sl, idx):
    if sl.get('solo_titulo'):      # portada de video narrado: solo el título, subido y centrado, sin logo ni textos de apoyo
        head = title_html(need(sl, 'title', 'cover'), 'h1', sl.get('pill'))
        return f'''
<section class="slide cover top">
  <div class="hero">{head}<span class="caret" style="display:none"></span></div>
</section>''', 0.0
    kicker = esc(need(sl, 'kicker', 'cover')); title = rich(need(sl, 'title', 'cover')); lead = esc(sl.get('lead', ''))
    lead_html = f'<p class="lead a" style="--d:5">{lead}</p>' if lead else ''
    html = f'''
<section class="slide cover">
  <div class="clogo a" style="--d:0">{LOGO}</div>
  <div class="hero">
    <div class="kicker a" style="--d:1">// {kicker}</div>
    <h1 class="a" style="--d:3;margin-top:30px">{title}<span class="caret"></span></h1>
    {lead_html}
  </div>
  <div class="foot a" style="--d:6">{{HANDLE}}</div>
</section>'''
    return html, 0.0


def L_cycle(sl, idx):
    nodes = need(sl, 'nodes', 'cycle'); n = len(nodes)
    if not 3 <= n <= 6: raise SpecError('cycle: usa entre 3 y 6 nodos')
    cx, cy, R, NR = 456, 470, (255 if n >= 5 else 270), 52   # círculo algo menor con 5-6 nodos: deja sitio a las etiquetas laterales
    step = 1.1 if n <= 5 else 0.9
    v = []; delta = (NR + 14) / R; span = 2 * math.pi / n
    for i, nd in enumerate(nodes):
        th = math.radians(-45 if n == 4 else -90) + span * i
        x, y = cx + R * math.cos(th), cy + R * math.sin(th)
        t = 0.2 + i * step
        a0, a1 = th + delta, th + span - delta
        p0 = (cx + R * math.cos(a0), cy + R * math.sin(a0)); p1 = (cx + R * math.cos(a1), cy + R * math.sin(a1))
        v.append(f'<path class="draw" pathLength="1" style="--t:{t+0.55:.2f}s" d="M{p0[0]:.1f} {p0[1]:.1f} A{R} {R} 0 0 1 {p1[0]:.1f} {p1[1]:.1f}" fill="none" stroke="{PINK}" stroke-width="4" stroke-linecap="round"/>')
        tx, ty = -math.sin(a1), math.cos(a1); nx, ny = math.cos(a1), math.sin(a1)
        tip = (p1[0] + tx * 12, p1[1] + ty * 12); b = (p1[0] - tx * 8, p1[1] - ty * 8)
        v.append(G(f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {b[0]+nx*11:.1f},{b[1]+ny*11:.1f} {b[0]-nx*11:.1f},{b[1]-ny*11:.1f}" fill="{PINK}"/>', t + 1.35, 'fade'))
        v.append(G(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{NR}" fill="{PANEL}" stroke="{VIO}" stroke-width="3"/>' + gi(nd['icon'], x - 24, y - 24, 48, VIO, 1.7), t, 'pop'))
        lab, sub = nd['label'], nd.get('sub', '')
        c, s_ = math.cos(th), math.sin(th)
        need_w = max(len(lab) * 16.5, len(sub) * 12.6)          # ancho aproximado de la etiqueta
        avail = (912 - (x + NR + 14)) if c > 0 else (x - NR - 14)
        side = abs(c) > 0.85 or (n == 4 and abs(c) > 0.5)
        if s_ < -0.85 or (side and need_w > avail and s_ < 0):      # arriba
            ls = text(f'{x:.1f}', f'{y-NR-20:.1f}', lab, 32, 700, INK, 'middle') + (text(f'{x:.1f}', f'{y-NR-56:.1f}', sub, 22, 400, MUTE, 'middle', True) if sub else '')
        elif side and need_w <= avail:                                 # a un lado
            sx, anc = (x + NR + 14, 'start') if c > 0 else (x - NR - 14, 'end')
            ls = text(f'{sx:.1f}', f'{y+4:.1f}', lab, 30, 700, INK, anc) + (text(f'{sx:.1f}', f'{y+34:.1f}', sub, 21, 400, MUTE, anc, True) if sub else '')
        else:                                                          # abajo
            ls = text(f'{x:.1f}', f'{y+NR+40:.1f}', lab, 32, 700, INK, 'middle') + (text(f'{x:.1f}', f'{y+NR+72:.1f}', sub, 22, 400, MUTE, 'middle', True) if sub else '')
        v.append(G(ls, t + 0.15))
    center = sl.get('center', '')
    v.append(G(f'<g class="spin">{gi("refresh-cw", cx-40, cy-62 if center else cy-40, 80, VIO, 1.6)}</g>' + (text(cx, cy + 62, center, 44, 700, INK, 'middle') if center else ''), 0.1, 'pop'))
    end_draw = 0.2 + (n - 1) * step + 0.55 + 1.0
    v.append(f'<g class="orbit" style="--t:{end_draw:.2f}s"><circle cx="{cx}" cy="{cy-R}" r="12" fill="{PINK}"/><circle cx="{cx}" cy="{cy-R}" r="28" fill="{PINK}" opacity=".2"/></g>')
    end = end_draw
    if sl.get('caption'):
        v.append(G(text(456, 900, '// ' + sl['caption'], 26, 400, MUTE, 'middle', True), end_draw)); end += 0.7
    return frame(sl, svgwrap(v), idx), end


def L_layers(sl, idx):
    layers = need(sl, 'layers', 'layers'); n = len(layers)
    if not 2 <= n <= 4: raise SpecError('layers: usa entre 2 y 4 capas')
    colors = [PINK, VIO, '#9a9aa5', '#74747f']
    gap = 16; h = (818 - gap * (n - 1)) / n
    wid = lambda y: 330 + (912 - 330) / 818 * (y - 20)
    compact = h < 220
    v = []; last = 0
    for i, ly in enumerate(layers):
        y0 = 20 + i * (h + gap); y1 = y0 + h; w0, w1 = wid(y0), wid(y1); col = colors[i]
        t = 0.2 + (n - 1 - i) * 1.3; last = max(last, t)
        pts = f'{456-w0/2:.1f},{y0:.1f} {456+w0/2:.1f},{y0:.1f} {456+w1/2:.1f},{y1:.1f} {456-w1/2:.1f},{y1:.1f}'
        b = f'<polygon points="{pts}" fill="{rgba(col, .14)}" stroke="{col}" stroke-width="2.5" stroke-linejoin="round"/>'
        if compact:
            b += gi(ly['icon'], 456 - 18, y0 + 20, 36, col, 1.8) + text(456, y0 + 96, ly['title'], 38, 700, INK, 'middle')
            b += text(456, y0 + 130, ly.get('sub', ''), 20, 400, MUTE, 'middle', True) + text(456, y0 + 166, ly.get('note', ''), 22, 700, col, 'middle', True)
        else:
            b += gi(ly['icon'], 456 - 22, y0 + 34, 44, col, 1.8) + text(456, y0 + 120, ly['title'], 42, 700, INK, 'middle')
            b += text(456, y0 + 160, ly.get('sub', ''), 22, 400, MUTE, 'middle', True) + text(456, y0 + 206, ly.get('note', ''), 24, 700, col, 'middle', True)
        v.append(G(b, t))
    t_axis = last + 1.4
    axis = sl.get('axis')
    if axis:
        cols = ''
        for k, (lab, txt_) in enumerate(zip(['ARRIBA', 'ABAJO'], axis)):
            x = k * 470
            cols += text(x, 894, lab, 22, 700, PINK, 'start', True, 'letter-spacing="3"') + text(x, 936, txt_, 27, 500, INK)
        v.append(G(cols, t_axis))
    end = t_axis + 0.7
    if sl.get('caption'):
        v.append(G(text(0, 990, '// ' + sl['caption'], 24, 400, MUTE, 'start', True), t_axis + 0.8)); end = t_axis + 1.5
    return frame(sl, svgwrap(v), idx), end


def L_flow(sl, idx):
    ins = need(sl, 'inputs', 'flow'); proc = need(sl, 'processor', 'flow'); res = need(sl, 'result', 'flow')
    n = len(ins)
    if n not in (2, 3): raise SpecError('flow: usa 2 o 3 entradas')
    gap = 36; w = (912 - gap * (n - 1)) / n
    targets = [330, 456, 582] if n == 3 else [380, 532]
    v = []
    for i, it in enumerate(ins):
        x = i * (w + gap); t = 0.2 + i * 0.35
        box = (f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="120" rx="30" fill="{PANEL}" stroke="{LINE}" stroke-width="3"/>'
               + gi(it['icon'], x + 28, 42, 36, VIO, 1.8) + text(x + 82, 72, it['label'], 30, 700))
        v.append(G(box, t))
        bx = x + w / 2
        v.append(f'<path class="draw" pathLength="1" style="--t:{t+0.7:.2f}s" d="M{bx:.1f} 120 C{bx:.1f} 215, {targets[i]} 205, {targets[i]} 300" fill="none" stroke="{PINK}" stroke-width="3.5" stroke-linecap="round"/>')
    judge = (f'<rect x="136" y="300" width="640" height="170" rx="38" fill="{PINK}"/>' + gi(proc['icon'], 190, 344, 74, BG, 1.7) +
             text(290, 392, proc['title'], 54, 700, BG) + text(290, 438, proc.get('sub', ''), 24, 500, BG, 'start', True))
    v.append(G(judge, 2.0, 'pop'))
    v.append(f'<path class="draw" pathLength="1" style="--t:2.9s" d="M456 478 L456 548" fill="none" stroke="{PINK}" stroke-width="3.5" stroke-linecap="round"/>')
    v.append(G(f'<polygon points="456,562 444,540 468,540" fill="{PINK}"/>', 3.5, 'fade'))
    of = int(res.get('of', 5)); filled = int(res.get('filled', of)); sw = (416 - (of - 1) * 10) / of
    card = f'<rect x="96" y="568" width="720" height="215" rx="34" fill="{PANEL}" stroke="{LINE}" stroke-width="3"/>'
    card += text(140, 624, res.get('label', 'RESULTADO').upper(), 21, 700, VIO, 'start', True, 'letter-spacing="3"')
    card += text(140, 712, res['value'], 88, 700)
    card += ''.join(f'<rect x="{360+k*(sw+10):.1f}" y="650" width="{sw:.1f}" height="30" rx="10" fill="{LINE}"/>' for k in range(of))
    card += ''.join(f'<rect class="seg" style="--t:{3.9+k*0.25:.2f}s" x="{360+k*(sw+10):.1f}" y="650" width="{sw:.1f}" height="30" rx="10" fill="{PINK}"/>' for k in range(filled))
    if res.get('quote'):
        card += text(140, 752, '“' + res['quote'] + '”', 22, 400, MUTE, 'start', True)
    v.append(G(card, 3.3))
    end = 5.0
    chips = sl.get('chips', [])
    if chips:
        v.append(G(text(0, 858, '// ' + sl.get('chips_title', 'a tener en cuenta'), 26, 500, VIO, 'start', True), 5.2))
        m = len(chips); cw = (912 - gap * (m - 1)) / m
        for i, c in enumerate(chips):
            x = i * (cw + gap)
            chip = (f'<rect x="{x:.1f}" y="885" width="{cw:.1f}" height="105" rx="26" fill="{rgba(VIO, .1)}" stroke="{rgba(VIO, .45)}" stroke-width="2"/>'
                    + gi(c['icon'], x + 20, 906, 32, VIO, 1.9) + text(x + 64, 930, c['label'], 24, 700) + text(x + 22, 968, c.get('sub', ''), 20, 400, MUTE, 'start', True))
            v.append(G(chip, 5.5 + i * 0.4))
        end = 5.5 + (m - 1) * 0.4 + 0.7
    return frame(sl, svgwrap(v), idx), end


def L_triangle(sl, idx):
    nodes = need(sl, 'nodes', 'triangle'); edges = need(sl, 'edges', 'triangle')
    if len(nodes) != 3: raise SpecError('triangle: exactamente 3 nodos (arriba, abajo-izquierda, abajo-derecha)')
    Q, C, A = (456, 150), (130, 700), (782, 700); NR = 78
    def edge(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]; d = math.hypot(dx, dy); ux, uy = dx / d, dy / d
        return (p[0] + ux * (NR + 6), p[1] + uy * (NR + 6), q[0] - ux * (NR + 6), q[1] - uy * (NR + 6))
    pts = [Q, C, A]; v = []
    for p, q, t in [(Q, C, 1.5), (C, A, 3.0), (A, Q, 4.5)]:
        x0, y0, x1, y1 = edge(p, q)
        v.append(f'<path class="draw" pathLength="1" style="--t:{t}s" d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" fill="none" stroke="{PINK}" stroke-width="4" stroke-linecap="round"/>')
    for k, (pt, nd) in enumerate(zip(pts, nodes)):
        t = 0.2 + k * 0.5
        v.append(G(f'<circle cx="{pt[0]}" cy="{pt[1]}" r="{NR}" fill="{PANEL}" stroke="{VIO}" stroke-width="3"/>' + gi(nd['icon'], pt[0] - 32, pt[1] - 32, 64, VIO, 1.7), t, 'pop'))
        ly = pt[1] - NR - 20 if k == 0 else pt[1] + NR + 44
        v.append(G(text(pt[0], ly, nd['label'], 34, 700, INK, 'middle'), t + 0.15))
    def pill(cx_, cy_, l1, l2, t):
        return G(f'<rect x="{cx_-122}" y="{cy_-42}" width="244" height="84" rx="26" fill="{PINK}"/>' + text(cx_, cy_ - 4, l1, 22, 700, BG, 'middle', True) + text(cx_, cy_ + 26, l2, 22, 700, BG, 'middle', True), t, 'pop')
    v += [pill(293, 425, *edges['left'], 2.6), pill(456, 700, *edges['bottom'], 4.1), pill(619, 425, *edges['right'], 5.6)]
    end = 6.3
    for i, q in enumerate(sl.get('questions', [])):
        y = 900 + i * 44; t = 6.3 + i * 0.4
        v.append(G(f'<circle cx="8" cy="{y-9}" r="6" fill="{PINK}"/>' + text(30, y, q['label'], 24, 700) + text(430, y, q['text'], 22, 400, MUTE, 'start', True), t))
        end = t + 0.7
    return frame(sl, svgwrap(v), idx), end


def L_bars(sl, idx):
    cats = need(sl, 'categories', 'bars'); n = len(cats)
    if not 3 <= n <= 5: raise SpecError('bars: usa entre 3 y 5 categorías')
    legend = sl.get('legend', ['antes', 'después'])
    BASEY, H = 640, 520
    yv = lambda x: BASEY - x / 100 * H
    x_left, width = 90, 822; gw = width / n; bw = min(80, (gw - 36) / 2)
    v = []
    hi = sl.get('highlight')
    tb = 0.3 + n * 0.55 + 0.8
    if hi is not None:
        v.append(G(f'<rect x="{x_left+hi*gw+4:.1f}" y="96" width="{gw-8:.1f}" height="{BASEY-96+60}" rx="28" fill="{rgba(PINK, .09)}" stroke="{rgba(PINK, .35)}" stroke-width="2"/>', tb + 1.0, 'fade'))
    for g in (0, 25, 50, 75, 100):
        y = yv(g)
        v.append(f'<line x1="70" x2="912" y1="{y}" y2="{y}" stroke="{LINE}" stroke-width="2"/>' + text(0, y + 8, str(g), 20, 400, MUTE, 'start', True))
    for i, c in enumerate(cats):
        x0 = x_left + i * gw; t = 0.3 + i * 0.55
        for k, (val, fill, tc) in enumerate([(c['a'], DIMVIO, '#c9c0ee'), (c['b'], PINK, BG)]):
            bx = x0 + (gw - 2 * bw - 10) / 2 + k * (bw + 10)
            v.append(f'<rect class="bar" style="--t:{t + k*0.25:.2f}s" x="{bx:.1f}" y="{yv(val):.1f}" width="{bw:.1f}" height="{val/100*H:.1f}" rx="10" fill="{fill}"/>')
            v.append(G(text(bx + bw / 2, yv(val) + 40, str(val), 26, 700, tc, 'middle', True), t + k * 0.25 + 0.8, 'fade'))
        v.append(G(text(x0 + gw / 2, BASEY + 46, c['label'], 24, 700, INK, 'middle'), t + 0.4, 'fade'))
    th = sl.get('threshold')
    if th:
        ty = yv(th['value'])
        v.append(f'<line class="draw" pathLength="1" style="--t:{tb:.2f}s" x1="70" x2="912" y1="{ty}" y2="{ty}" stroke="{VIO}" stroke-width="3"/>')
        v.append(G(text(92, ty - 12, th.get('label', f"umbral: {th['value']}"), 20, 700, VIO, 'start', True), tb + 0.8, 'fade'))
    v.append(G(f'<rect x="90" y="30" width="26" height="26" rx="8" fill="{DIMVIO}"/>' + text(126, 52, legend[0], 24, 700, MUTE, 'start', True) +
               f'<rect x="{190 + 12*max(0, len(legend[0])-2)}" y="30" width="26" height="26" rx="8" fill="{PINK}"/>' + text(226 + 12 * max(0, len(legend[0]) - 2), 52, legend[1], 24, 700, INK, 'start', True), 0.1, 'fade'))
    end = tb + 1.0
    co = sl.get('callout')
    if co:
        t = tb + 2.0
        al = (f'<rect x="0" y="755" width="912" height="190" rx="36" fill="{PANEL}" stroke="{PINK}" stroke-width="3"/>'
              f'<rect x="34" y="800" width="100" height="100" rx="30" fill="{rgba(PINK, .15)}" stroke="{PINK}" stroke-width="2"/>' + gi(co.get('icon', 'triangle-alert'), 56, 822, 56, PINK, 1.7) +
              text(166, 818, co['line1'], 33, 700) + text(166, 862, co['line2'], 33, 700, PINK) + (text(166, 904, '// ' + co['note'], 22, 400, MUTE, 'start', True) if co.get('note') else ''))
        v.append(G(al, t)); end = t + 0.8
    if sl.get('example_data', True):
        v.append(G(text(912, 985, '// datos de ejemplo', 20, 400, MUTE, 'end', True), end, 'fade')); end += 0.6
    return frame(sl, svgwrap(v), idx), end


def L_code(sl, idx):
    lines = need(sl, 'lines', 'code')
    rows = []; t = 0.3
    for ln in lines:
        raw = ln
        # escapar solo el texto, conservando el marcado
        parts = re.split(r'(\{[pvm]:[^}]*\})', raw)
        html = ''.join(
            (f'<span class="tk-{p[1]}">{esc(p[3:-1])}</span>' if re.fullmatch(r'\{[pvm]:[^}]*\}', p) else esc(p)) for p in parts)
        n = len(re.sub(r'\{[pvm]:([^}]*)\}', r'\1', raw))
        if n > 46: print(f'AVISO code slide {idx}: línea de {n} caracteres puede cortarse (máx. ~46): {raw[:40]}…', file=sys.stderr)
        rows.append(f'<span class="ln" style="--n:{max(n,1)};--t:{t:.2f}s">{html or "&nbsp;"}</span>')
        t += 0.35 + n * 0.022
    fn = esc(sl.get('filename', 'ejemplo.txt'))
    body = f'<div class="mid"><div class="win g" style="--t:0s"><div class="wbar"><i></i><i></i><i></i><span>{fn}</span></div><div class="code">{"".join(rows)}</div></div>'
    end = t + 0.6
    if sl.get('caption'):
        body += f'<div class="note" style="--t:{end:.2f}s">// {esc(sl["caption"])}</div>'; end += 0.8
    body += '</div>'
    return frame(sl, body, idx), end


def L_versus(sl, idx):
    L, Rr = need(sl, 'left', 'versus'), need(sl, 'right', 'versus')
    cols = ''; end = 0
    for side, cls, base in ((L, 'l', 0.2), (Rr, 'r', 0.5)):
        items = side.get('items', [])
        if not 2 <= len(items) <= 5: raise SpecError('versus: cada lado necesita entre 2 y 5 ítems')
        its = ''.join(f'<div class="it" style="--t:{base+1.0+i*0.7:.2f}s"><i></i><span>{esc(x)}</span></div>' for i, x in enumerate(items))
        cols += f'<div class="col {cls}" style="--t:{base:.2f}s"><div class="ic">{icon_html(side["icon"])}</div><h3>{esc(side["title"])}</h3>{its}</div>'
        end = max(end, base + 1.0 + len(items) * 0.7 + 0.7)
    body = f'<div class="mid"><div class="vs">{cols}<div class="vsb">vs</div></div>'
    if sl.get('caption'):
        body += f'<div class="note" style="--t:{end:.2f}s">// {esc(sl["caption"])}</div>'; end += 0.8
    body += '</div>'
    return frame(sl, body, idx), end


def L_list(sl, idx):
    items = need(sl, 'items', 'list')
    if not 3 <= len(items) <= 5: raise SpecError('list: usa entre 3 y 5 ítems')
    rows = ''.join(f'<div class="row rg" style="--t:{0.2+i*0.7:.2f}s;--f:{1.0+i*0.7:.2f}s"><div class="ico">{icon_html(it["icon"])}</div><div class="txt"><span class="name">{esc(it["name"])}</span><div class="desc">// {esc(it["desc"])}</div></div></div>' for i, it in enumerate(items))
    t_cta = 0.2 + (len(items) - 1) * 0.7 + 1.8
    cta = esc(sl.get('cta', 'sígueme para más contenido tech'))
    body = f'<div class="tree">{rows}</div><div class="cta-pill g" style="--t:{t_cta:.2f}s"><b>$</b> {cta}</div>'
    return frame(sl, body, idx), t_cta + 0.8


def _code_row(raw):
    parts = re.split(r'(\{[pvm]:[^}]*\})', raw)
    html = ''.join((f'<span class="tk-{p[1]}">{esc(p[3:-1])}</span>' if re.fullmatch(r'\{[pvm]:[^}]*\}', p) else esc(p)) for p in parts)
    return html, len(re.sub(r'\{[pvm]:([^}]*)\}', r'\1', raw))


def L_code_focus(sl, idx):
    """Código que se escribe y se explica: cada paso resalta unas líneas; la salida (resultado) aparece por pasos.
    steps[{lines:[2,3], peso:2.0, note:'opcional'}]   salida:[ "texto" | {t:"texto", paso:2} ]  (paso = 1..n, por defecto el último)"""
    lines = need(sl, 'lines', 'code_focus'); steps = need(sl, 'steps', 'code_focus')
    if not 1 <= len(steps) <= 6: raise SpecError('code_focus: usa entre 1 y 6 pasos')
    if len(lines) > 14: raise SpecError('code_focus: máximo 14 líneas (en el celular no se leería)')
    t = 0.3; ts = []
    for ln in lines:
        html, n = _code_row(ln)
        if n > 46: print(f'AVISO code_focus slide {idx}: línea de {n} caracteres puede cortarse (máx. ~46): {ln[:40]}…', file=sys.stderr)
        ts.append(t); t += 0.22 + n * 0.012
    t_steps = max(t + 0.5, float(sl.get('inicio', 0)))   # inicio = segundos de voz antes del primer paso
    nominal = [float(st.get('peso', 1.5 + 0.35 * len(str(st.get('note', '')).split()))) for st in steps]
    starts, acc = [], t_steps
    for d in nominal: starts.append(acc); acc += d
    hl_for = {}
    for si, st in enumerate(steps):
        for ln_no in st.get('lines', []):
            if not 1 <= ln_no <= len(lines): raise SpecError(f'code_focus: el paso {si+1} señala la línea {ln_no}, que no existe (1..{len(lines)})')
            hl_for.setdefault(ln_no - 1, []).append(si)
    last = len(steps) - 1
    rows = []
    for i, ln in enumerate(lines):
        html, n = _code_row(ln)
        hl = ''.join(f'<div class="hl{" keep" if si == last else ""}" style="--t:{starts[si]:.2f}s;--dur:{nominal[si]:.2f}s"></div>' for si in hl_for.get(i, []))
        rows.append(f'<div class="lr"><span class="ln" style="--n:{max(n,1)};--t:{ts[i]:.2f}s">{html or "&nbsp;"}</span>{hl}</div>')
    notes = ''.join(f'<div class="cnote{" keep" if si == last else ""}" style="--t:{starts[si]:.2f}s;--dur:{nominal[si]:.2f}s"><span>{rich(st["note"])}</span></div>'
                    for si, st in enumerate(steps) if st.get('note'))
    nbox = f'<div class="nbox">{notes}</div>' if notes else ''
    out_rows, pasos = [], []
    for k, o in enumerate(sl.get('salida', [])):
        txt, paso = (o, len(steps)) if isinstance(o, str) else (o['t'], int(o.get('paso', len(steps))))
        if not 1 <= paso <= len(steps): raise SpecError(f'code_focus: la salida {k+1} usa el paso {paso}, que no existe')
        html, _ = _code_row(txt); pasos.append(paso)
        out_rows.append(f'<div class="orow" style="--t:{starts[paso-1] + 0.15:.2f}s">{html or "&nbsp;"}</div>')
    salida = f'<div class="out g" style="--t:{starts[min(pasos) - 1]:.2f}s">{"".join(out_rows)}</div>' if out_rows else ''
    fn = esc(sl.get('filename', 'ejemplo.py'))
    body = (f'<div class="mid"><div class="win g" style="--t:0s"><div class="wbar"><i></i><i></i><i></i><span>{fn}</span></div>'
            f'<div class="code">{"".join(rows)}</div></div>{salida}{nbox}</div>')
    return frame(sl, body, idx), acc


def L_outro(sl, idx):
    """Cierre de marca: CARLICODE se escribe letra por letra, un brillo recorre las letras y un cursor hace click en «sígueme»."""
    word = sl.get('word', 'CARLICODE'); split = int(sl.get('split', 5))
    follow = esc(sl.get('follow', 'sígueme')); done = esc(sl.get('done', 'siguiendo'))
    t0, step = 0.3, 0.13
    letters = ''
    for i, ch in enumerate(word):
        cls = 'li pk' if i >= split else 'li'
        t_in = t0 + i * step
        letters += f'<span class="lw" style="--t:{t0 + len(word) * step + 0.5 + i * 0.09:.2f}s"><span class="{cls}" style="--t:{t_in:.2f}s">{esc(ch)}</span></span>'
    t_pill = t0 + len(word) * step + 0.4
    t_ptr = t_pill + 0.9
    t_click = t_ptr + 0.95
    check = ('<svg viewBox="0 0 24 24" fill="none" stroke="#09090b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" width="34" height="34">'
             '<path d="M20 6 9 17l-5-5"/></svg>')
    cursor = ('<svg viewBox="0 0 24 24" width="72" height="72"><path d="M5 3l14 8-6.2 1.6L9.6 19z" fill="#f4f4f5" stroke="#09090b" stroke-width="1.4" stroke-linejoin="round"/></svg>')
    html = f'''
<section class="slide outro">
  <div class="oword">{letters}<span class="caret oc"></span></div>
  <div class="ofollow">
    <div class="fpw" style="--t:{t_click:.2f}s">
      <div class="fp g" style="--t:{t_pill:.2f}s"><b>+</b> {follow}</div>
      <div class="fp on" style="--t:{t_click + 0.05:.2f}s">{check} {done}</div>
    </div>
    <div class="ripple" style="--t:{t_click:.2f}s"></div>
    <div class="ptr" style="--t:{t_ptr:.2f}s">{cursor}</div>
  </div>
</section>'''
    return html, t_click + 1.2


# ----------------------------------------------------------------- video de concepto (diagramas grandes + tramos con cara)
COLORS = {'pink': PINK, 'violet': VIO, 'yellow': '#ffd60a', 'gray': '#6b6b76', 'white': INK}

def _col(c): return COLORS.get(c, c or VIO)


def _diagram_item(it):
    """Devuelve (svg, es_pop) de un elemento del diagrama."""
    k = it['k']; col = _col(it.get('color'))
    if k == 'box':
        x, y, w, h = it['x'], it['y'], it['w'], it['h']
        ipx = it.get('ipx', 64); lpx = it.get('lpx', 36)
        fill = rgba(col, .22) if it.get('solid') else PANEL
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="30" fill="{fill}" stroke="{col}" stroke-width="4"/>'
        has_icon = bool(it.get('icon')); sub = it.get('sub', '')
        block = (ipx + 14 if has_icon else 0) + lpx + (34 if sub else 0)
        y0 = y + 26 if it.get('top') else y + (h - block) / 2
        if has_icon: s += gi(it['icon'], x + w / 2 - ipx / 2, y0, ipx, col, 1.7)
        ly = y0 + (ipx + 14 if has_icon else 0) + lpx * 0.82
        s += text(x + w / 2, f'{ly:.1f}', it['label'], lpx, 800, INK, 'middle', extra='style="font-family:Poppins,sans-serif"')
        if sub: s += text(x + w / 2, f'{ly + 34:.1f}', sub, it.get('spx', 24), 400, MUTE, 'middle', True)
        return s, True
    if k == 'dbox':
        x, y, w, h = it['x'], it['y'], it['w'], it['h']
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="34" fill="{rgba(col, .05)}" stroke="{col}" stroke-width="3" stroke-dasharray="16 12"/>'
        if it.get('label'):
            s += (text(x + w / 2, y + 42, '// ' + it['label'], it.get('lpx', 26), 500, col, 'middle', True) if it.get('center')
                  else text(x + 28, y + 42, '// ' + it['label'], it.get('lpx', 26), 500, col, 'start', True))
        return s, False
    if k == 'arrow':
        x1, y1, x2, y2 = it['x1'], it['y1'], it['x2'], it['y2']; wd = it.get('w', 5)
        dash = ' stroke-dasharray="14 12"' if it.get('dash') else ''
        ang = math.atan2(y2 - y1, x2 - x1); L = 24
        hx, hy = x2 - math.cos(ang) * 2, y2 - math.sin(ang) * 2
        p1 = (hx - math.cos(ang) * L + math.cos(ang + math.pi / 2) * 13, hy - math.sin(ang) * L + math.sin(ang + math.pi / 2) * 13)
        p2 = (hx - math.cos(ang) * L - math.cos(ang + math.pi / 2) * 13, hy - math.sin(ang) * L - math.sin(ang + math.pi / 2) * 13)
        base = (hx - math.cos(ang) * L * 0.6, hy - math.sin(ang) * L * 0.6)
        s = (f'<path d="M{x1} {y1} L{base[0]:.1f} {base[1]:.1f}" stroke="{col}" stroke-width="{wd}" stroke-linecap="round" fill="none"{dash}/>'
             f'<polygon points="{hx:.1f},{hy:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{col}"/>')
        return s, False
    if k == 'text':
        fam = ' style="font-family:Poppins,sans-serif"' if it.get('poppins') else ''
        return text(it['x'], it['y'], it['s'], it.get('size', 40), it.get('weight', 800 if it.get('poppins') else 600), col if it.get('color') else INK,
                    it.get('anchor', 'middle'), bool(it.get('mono')), fam), False
    if k == 'pill':
        x, y, sz = it['x'], it['y'], it.get('size', 36); s_ = it['s'].upper()
        w = len(s_) * sz * 0.66 + 70
        s = (f'<g transform="rotate({it.get("rot", -2)} {x} {y})"><rect x="{x - w/2 + 5:.1f}" y="{y - sz*0.95 + 7:.1f}" width="{w:.1f}" height="{sz*1.7:.1f}" rx="22" fill="#000" opacity=".85"/>'
             f'<rect x="{x - w/2:.1f}" y="{y - sz*0.95:.1f}" width="{w:.1f}" height="{sz*1.7:.1f}" rx="22" fill="#ffd60a" stroke="#000" stroke-width="5"/>'
             + text(x, f'{y + sz*0.28:.1f}', s_, sz, 800, BG, 'middle', extra='style="font-family:Poppins,sans-serif"') + '</g>')
        return s, True
    if k == 'icon':
        return gi(it['name'], it['x'] - it['size'] / 2, it['y'] - it['size'] / 2, it['size'], col, it.get('sw', 1.6)), True
    if k == 'poly':
        pts = ' '.join(f'{a},{b}' for a, b in it['pts'])
        return f'<polygon points="{pts}" fill="{rgba(col, it.get("alpha", .14))}" stroke="{col}" stroke-width="4" stroke-linejoin="round"/>', False
    if k == 'wave':
        y = it['y']
        def wv(yy, amp, ph): return 'M-20 %s ' % yy + ' '.join(f'Q{x+40} {yy + (amp if (i + ph) % 2 == 0 else -amp)} {x+80} {yy}' for i, x in enumerate(range(-20, 1040, 80)))
        return (f'<path d="{wv(y, 18, 0)}" stroke="{col}" stroke-width="5" fill="none" opacity=".55"/>'
                f'<path d="{wv(y + 36, 18, 1)}" stroke="{col}" stroke-width="5" fill="none" opacity=".3"/>'), False
    raise SpecError(f"diagram: elemento '{k}' desconocido (box, dbox, arrow, text, pill, icon, poly, wave)")


def L_diagram(sl, idx):
    """Diagrama grande (lienzo 1000x1000) que se construye elemento por elemento. Cada elemento: k + parámetros;
    't' fija su segundo, 'dt' es la espera hasta el siguiente (0.5 por defecto), 'cae' = segundo en que se cae del lienzo."""
    items = need(sl, 'items', 'diagram'); v = []; t = 0.3; end = 0.0
    for it in items:
        t_it = float(it['t']) if 't' in it else t
        if 't' not in it: t += float(it.get('dt', 0.5))
        svg, pop = _diagram_item(it)
        if it['k'] == 'arrow':
            v.append(G(svg, t_it, 'fade'))
        else:
            v.append(G(svg, t_it, 'pop' if pop else 'fade'))
        if it.get('cae') is not None:   # se envuelve DESPUÉS de G para que la caída afecte al elemento ya visible
            v[-1] = f'<g class="fall" style="--t:{float(it["cae"]):.2f}s">{v[-1]}</g>'
            end = max(end, float(it['cae']) + 1.0)
        end = max(end, t_it + 0.8)
    sc = float(sl.get('escala', 1))
    body = (f'<div class="viz big"><svg viewBox="0 0 1000 1000" style="width:{1000*sc:.0f}px;height:{1000*sc:.0f}px;margin-left:{-(sc-1)*500:.0f}px">'
            f'{"".join(v)}</svg></div>')
    return frame(dict(sl, sin_handle=True), body, idx), end


def L_cara(sl, idx):
    """Tramo donde apareces tú. Por defecto solo queda el título (ella monta su video encima al editar).
    Con "marco": true se dibuja el marco "TU CARA AQUÍ" con la duración y una barra de progreso."""
    if not sl.get('marco'):
        return frame(dict(sl, sin_handle=True), '', idx), 0.0
    dur = float(sl.get('dur', 0)); mm = f'{int(dur) // 60}:{int(dur) % 60:02d}'
    person = gi('user', 0, 0, 120, VIO, 1.5)
    body = (f'<div class="face"><div class="fbox"><svg viewBox="0 0 120 120" width="150" height="150">{person}</svg>'
            f'<div class="flab">TU CARA AQUÍ</div><div class="fsub">{mm} · {esc(sl.get("nota", "hablas a cámara"))}</div></div>'
            f'<div class="fbar"><i style="--dur:{dur:.2f}s"></i></div></div>')
    return frame(dict(sl, sin_handle=True), body, idx), 0.0


LAYOUTS = {'cover': L_cover, 'cycle': L_cycle, 'layers': L_layers, 'flow': L_flow, 'triangle': L_triangle,
           'bars': L_bars, 'code': L_code, 'code_focus': L_code_focus, 'outro': L_outro, 'diagram': L_diagram, 'cara': L_cara, 'versus': L_versus, 'list': L_list}


# ----------------------------------------------------------------- ensamblado
def build(spec_path, out_dir=None):
    spec = json.load(open(spec_path))
    slides = need(spec, 'slides', 'spec')
    handle = spec.get('handle', '@carli.code')
    if len(slides) < 4 or len(slides) > 9:
        raise SpecError(f'Usa entre 4 y 9 slides (tienes {len(slides)})')
    if slides[0]['type'] != 'cover': raise SpecError("La primera slide debe ser de tipo 'cover'")
    if slides[-1]['type'] != 'list': raise SpecError("La última slide debe ser de tipo 'list' (checklist + CTA)")
    out_dir = out_dir or os.path.dirname(os.path.abspath(spec_path))
    os.makedirs(out_dir, exist_ok=True)
    parts, meta = [], []
    for i, sl in enumerate(slides, 1):
        t = sl.get('type')
        if t not in LAYOUTS: raise SpecError(f"Slide {i}: tipo '{t}' desconocido. Tipos: {sorted(LAYOUTS)}")
        html, end = LAYOUTS[t](sl, i)
        parts.append(html.replace('{HANDLE}', esc(handle)))
        dur = max(MIN_SECONDS, math.ceil(end + HOLD))
        meta.append({'index': i, 'type': t, 'duration': dur, 'offset': 3 if t == 'cover' else 0, 'animation_end': round(end, 2)})
    css = open(os.path.join(ASSETS, 'tech.css')).read()
    js = re.sub(r'const DUR=\[[^\]]*\];', 'const DUR=' + json.dumps([m['duration'] for m in meta]) + ';', open(os.path.join(ASSETS, 'tech.js')).read())
    title = esc(spec.get('title', 'Carrusel'))
    page = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<div id="viewport"><div id="stage"><div class="bg"><div class="blob b1"></div><div class="blob b2"></div></div>{''.join(parts)}</div></div>
<div id="ui"><button id="prev">←</button><div id="dots"></div><button id="play">⏸ Pausa</button><button id="next">→</button><button id="loop">Reiniciar</button></div>
<script>{js}</script></body></html>'''
    html_path = os.path.join(out_dir, 'carousel.html')
    open(html_path, 'w').write(page)
    json.dump({'title': spec.get('title'), 'slides': meta}, open(os.path.join(out_dir, 'meta.json'), 'w'), indent=2, ensure_ascii=False)
    return html_path, meta


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    try:
        path, meta = build(sys.argv[1], out)
    except SpecError as e:
        print(f'ERROR de spec: {e}', file=sys.stderr); sys.exit(2)
    print(path)
    for m in meta:
        print(f"  slide {m['index']} ({m['type']}): {m['duration']} s")
