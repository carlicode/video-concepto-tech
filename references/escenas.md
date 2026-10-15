# Escenas del video (spec JSON)

`spec.json`:
```json
{"titulo": "...", "slug": "event-loop", "palabra_clave": "event loop", "handle": "@carli.code",
 "ritmo": 2.6, "pausa": 0.5,
 "escenas": [ {"id": "gancho", "type": "cover", "voz": "...", "pantalla": "...", "cara": true, "kicker": "...", "title": "..."} ]}
```
Campos de TODA escena: `id` (corto, sin espacios: sale en el nombre del clip), `type`, `voz` (texto exacto que dirás; `[entre corchetes]` = indicaciones que no se leen ni se cuentan), `pantalla` (1 línea: qué se ve; sirve para el borrador, NO va en guion.txt), `cara` (true si apareces en cámara), `dur` (opcional, fuerza segundos).
La duración de la escena sale de las palabras de `voz` (`ritmo` = palabras/segundo, 2.6 por defecto ≈ 156/min; `pausa` se suma). Las animaciones se reparten solas para terminar ~1 s antes del fin de la voz.

## Tipos (mismos campos que carrusel-tech, ver sus límites de texto)
| type | Úsalo para | Campos |
|---|---|---|
| `cover` | Gancho (siempre primera). Fija desde el primer cuadro | `kicker`, `title` (`*palabra*` en rosa, `\n` salto), `lead` |
| `code_focus` | **El centro del formato.** Código que se escribe y luego se explica línea por línea | `filename`, `lines[]` (≤14 líneas, ≤40 caracteres, marcas `{p:rosa}` `{v:violeta}` `{m:gris}`), `steps[{lines:[2,3], note:"texto corto con *rosa*", peso}]` (1–6 pasos; `lines` = números desde 1; `peso` = segundos relativos, opcional) |
| `code` | Código/terminal que solo se escribe, sin resaltar | `filename`, `lines[]` (≤46), `caption` |
| `cycle` | Loops y ciclos (3–6 nodos) | `nodes[{icon,label,sub}]`, `center`, `caption` |
| `layers` | Capas y niveles (2–4) | `layers[{icon,title,sub,note}]`, `axis[2]`, `caption` |
| `flow` | Entradas → proceso → resultado | `inputs[2-3]`, `processor`, `result`, `chips` |
| `triangle` | Relación entre 3 cosas | `nodes[3]`, `edges`, `questions` |
| `bars` | Comparar números (0–100) | `categories`, `legend`, `threshold`, `callout`, `example_data` |
| `versus` | A contra B, mito vs. realidad | `left{icon,title,items[2-5]}`, `right` |
| `list` | Resumen + CTA (última escena) | `items[3-5]{icon,name,desc}`, `cta` |
Todas menos `cover` llevan `kicker` y `title` (≤35 caracteres, una palabra en *rosa*). Iconos Lucide: `ls assets/icons`.

## Cómo elegir
- Cada concepto se cuenta con **el visual que muestra su mecanismo real** (el event loop es `cycle`; una petición HTTP es `flow`; capas de memoria es `layers`).
- Si el concepto tiene código, hay al menos una `code_focus`; es lo que distingue al canal. 8–12 líneas, un paso por idea, notas de ≤8 palabras.
- Estructura base (45–90 s, 5–7 escenas): `cover` (gancho) → problema/idea → 1–2 escenas de mecanismo (esquema) → `code_focus` → error común o `versus` → `list` (resumen + pregunta).
- No repitas el mismo tipo dos veces seguidas. Una idea por escena, ≥4 s y ≤ ~20 s cada una.
- Ajuste de tiempos: `python3 scripts/build_video.py spec.json --plan` muestra inicio/fin de cada escena y en qué segundo aparece cada elemento. Avisa si una escena va muy rápida (poca voz para tanto contenido: alarga la voz o quita elementos) o muy lenta (divide o añade contenido).

## Añadidos para video narrado (ver "Formato por defecto" en SKILL.md)
- `cover` + `"solo_titulo": true` → solo `title`, subido, sin logo/kicker/lead/handle. Con `"dur": 5`.
- Todas las escenas con `frame`: `kicker` es **opcional** (omítelo) y `"sin_handle": true` quita `@carli.code`.
- `code_focus` (≤14 líneas, ≤46 caracteres): `steps[{lines:[2], peso:2}]` resalta líneas (la `note` es opcional y por defecto no se usa) y `salida` es el resultado:
  `"salida": ["texto", {"t":"{p:True}", "paso":2}]` → cada línea aparece en el paso indicado (1..n; por defecto el último), con marcas `{p:rosa}` `{v:violeta}` `{m:gris}`. La salida se dibuja en un panel con borde rosa bajo el código; usa espacios para alinear columnas y deja en rosa lo que importa.
- `outro` (cierre de marca): `{"type":"outro","dur":5.5,"voz":"Sígueme para más contenido tech."}`. Opcionales: `word` (CARLICODE), `split` (letras en blanco antes de las rosas, 5), `follow` ("sígueme"), `done` ("siguiendo").
- `pill`: texto de la pastilla amarilla bajo el título (en `cover` con `solo_titulo` y en cualquier escena con título). Máx. ~24 caracteres, no repitas el título.
- Marcas de título: `*rosa*`, `~amarillo~`, `\n` = salto de línea (las líneas explícitas no se parten en la portada). Los títulos salen en mayúsculas automáticamente.

## Video de concepto (diagram + cara)
- `diagram`: `{"type":"diagram","dur":12,"title":"…","pill":"…","escala":1.0,"items":[…]}` (lienzo 1000×1000, y ≈ 600 a 1600 en pantalla). Elementos (`k`): `box{x,y,w,h,label,sub,icon,color,solid,ipx,lpx,top}`, `dbox{x,y,w,h,label,color,center}` (recuadro punteado), `arrow{x1,y1,x2,y2,color,dash}`, `text{x,y,s,size,color,poppins,mono}`, `pill{x,y,s,size,rot}` (sticker amarillo), `icon{name,x,y,size,color}`, `poly{pts,color,alpha}`, `wave{y,color}`. Tiempos: `t` (segundo), `dt` (espera al siguiente), `cae` (segundo en que cae); todos se reescalan a la duración. Colores: pink, violet, yellow, gray, o `#hex`.
- `cara`: `{"type":"cara","dur":6,"title":"…","cara":true,"voz":"[CARA] …"}`. Solo dibuja el título; `"marco": true` añade el marco "TU CARA AQUÍ" (+ `nota`).
- Títulos: `==x==` marcador amarillo, `*x*` rosa, `~x~` amarillo, `title_px`.
