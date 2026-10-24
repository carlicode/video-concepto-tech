# Layouts del carrusel (spec JSON)

El carrusel se describe con un JSON: `{"title": "...", "handle": "@carli.code", "slides": [ ... ]}`. Cada slide tiene un `type`. Ejemplo completo y probado: `example-evaluacion.json` (7 slides: cover, cycle, layers, flow, triangle, bars, list).

**Reglas generales**
- La **primera** slide es `cover` y la **última** es `list` (checklist + CTA). Entre 4 y 9 slides en total (ideal 6 a 8).
- `kicker` = etiqueta corta en minúsculas (se muestra como `// kicker`). `title` = título corto (máx. ~35 caracteres); marca con `*asteriscos*` la palabra clave que va en rosa. En `cover`, `\n` hace salto de línea.
- Textos cortos: los esquemas tienen poco espacio. Etiquetas ≤ 14 caracteres, subtítulos ≤ 18, descripciones de lista ≤ 34.
- `icon` = nombre de un icono Lucide de `assets/icons/` (`ls assets/icons`). Si no hay uno adecuado, `scripts/add_icon.sh nombre` lo descarga.
- Cada slide dura mínimo 10 s; el builder calcula la duración (fin de la animación + 3 s de pausa).
- Elige layouts variados: no repitas el mismo tipo dos veces seguidas.

## Cuándo usar cada layout
| type | Úsalo para | Campos principales |
|---|---|---|
| `cover` | Portada (siempre primera) | `kicker`, `title`, `lead` |
| `cycle` | Procesos que se repiten, ciclos, loops (3 a 6 pasos) | `nodes[{icon,label,sub}]`, `center`, `caption` |
| `layers` | Niveles, jerarquías, capas, costo vs. cobertura (2 a 4) | `layers[{icon,title,sub,note}]` (de arriba a abajo), `axis[2]`, `caption` |
| `flow` | Entradas → proceso → resultado (2 o 3 entradas) | `inputs[{icon,label}]`, `processor{icon,title,sub}`, `result{label,value,of,filled,quote}`, `chips_title`, `chips[{icon,label,sub}]` |
| `triangle` | Relación entre 3 elementos | `nodes[3]` (arriba, abajo-izq., abajo-der.), `edges{left,bottom,right}` (cada uno `[línea1,línea2]`), `questions[{label,text}]` |
| `bars` | Comparar dos versiones o grupos (3 a 5 categorías, valores 0-100) | `legend[2]`, `categories[{label,a,b}]`, `threshold{value,label}`, `highlight` (índice), `callout{icon,line1,line2,note}`, `example_data` |
| `code` | Prompts, comandos, configs, snippets | `filename`, `lines[]` (máx. 46 caracteres), `caption` |
| `versus` | A contra B, antes y después, mito y realidad | `left{icon,title,items[2-5]}`, `right{…}`, `caption` |
| `list` | Resumen en 3 a 5 puntos + CTA (siempre última) | `items[{icon,name,desc}]`, `cta` (opcional) |

## Notas por layout
- **cycle:** con 4 nodos se colocan en diagonal; con 5 o 6 en círculo clásico. Las etiquetas largas se mueven solas abajo o arriba si no caben.
- **layers:** se dibuja como pirámide; la primera capa del arreglo va arriba y en rosa, la segunda en violeta, las demás en grises. Con 4 capas el texto se compacta.
- **flow:** pensado para "evaluador", "pipeline", "clasificador". `result` es la tarjeta de salida con barra de segmentos (`filled` de `of`). `chips` es opcional.
- **bars:** si los números son inventados, deja `example_data: true` (muestra "// datos de ejemplo"); ponlo en `false` solo si son datos reales que dio el usuario.
- **code:** marcado dentro de las líneas: `{p:texto}` rosa, `{v:texto}` violeta, `{m:texto}` gris. Las líneas se escriben solas, una por una. Usa líneas vacías (`""`) para separar bloques.
- **versus:** cada ítem ≤ 28 caracteres para que no ocupe más de 2 líneas.
- **list:** el CTA por defecto es `sígueme para más contenido tech`. No lo cambies salvo que el usuario lo pida.

## Ejemplo mínimo
```json
{"title": "Prompts que funcionan", "slides": [
  {"type": "cover", "kicker": "ia · prompting", "title": "Cómo escribir\nprompts que\n*funcionan*", "lead": "estructura, ejemplos y pruebas"},
  {"type": "versus", "kicker": "antes y después", "title": "Vago vs *preciso*",
   "left": {"icon": "x", "title": "Prompt vago", "items": ["“Resume esto”", "Sin contexto"]},
   "right": {"icon": "circle-check", "title": "Prompt preciso", "items": ["Rol y objetivo", "Formato de salida"]}},
  {"type": "code", "kicker": "anatomía", "title": "Un prompt con *estructura*", "filename": "prompt.md",
   "lines": ["{v:# Rol}", "Eres analista de datos senior."]},
  {"type": "list", "kicker": "checklist", "title": "Antes de *enviar*",
   "items": [{"icon": "user", "name": "Define el rol", "desc": "quién responde"}, {"icon": "file-text", "name": "Da contexto", "desc": "datos y límites"}, {"icon": "list-checks", "name": "Pide el formato", "desc": "JSON, tabla, lista"}]}
]}
```
