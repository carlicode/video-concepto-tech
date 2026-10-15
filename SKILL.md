---
name: video-concepto-tech
description: Crea videos verticales (Reels/TikTok) de Carli Code (@carli.code) que explican un concepto de programación o IA con slides animados en HTML (código que se escribe y se resalta, esquemas) sincronizados con el guion de SU VOZ, con su cara solo en algunos momentos. Flujo de 3 pasos - 1) preguntas, 2) borrador segundo a segundo + guion de voz, 3) video completo + clips por escena + copy + guion, guardados en "Documentos/Contenido tech skill". Úsala cuando pida un video explicando un concepto, "video con mi voz", "reel de código", "explica X en video", "video con slides y voz", o diga "usa la skill de videos", aunque no nombre la skill. No es para carruseles sin voz (carrusel-tech) ni para guiones sueltos (guion-tiktok).
---

# Video de concepto tech con voz (Carli Code)

Idea: Carli da un tema, la skill construye **lo visual** (slides animados en el estilo de marca) con la duración y el ritmo de **su guion**; ella solo graba la voz (y aparece en cámara un par de veces). El centro del video es el código y los esquemas, no la cara.

Hay **tres pasos con puntos de control**. No saltes pasos: no se construye nada hasta que ella apruebe el borrador.

Todo en español. Estilo de marca: `references/style.md` (negro, rosa = lo que destaca, violeta = estructura, Space Grotesk + JetBrains Mono, iconos Lucide, sin emojis en el video).

## Dónde se guarda
Siempre en `~/Documents/Contenido tech skill/<slug>/` (si la carpeta no existe, créala; quien use la skill puede cambiar esta ruta aquí; crea la subcarpeta con el slug del tema en kebab-case, sin tildes). Contenido final:
```
<slug>/
├── video-completo.mp4        (todas las escenas pegadas, 1080x1920, 30 fps)
├── clips/01-gancho.mp4 …     (un clip por escena)
├── copy.txt                  (descripción con SEO + 5 hashtags)
├── guion.txt                 (solo el texto de la voz, para teleprompter)
├── portada.txt / portada.png (el título para poner de portada del video: texto + imagen 1080x1920)
└── fuente/ spec.json, video.html, meta.json   (para editar y re-exportar)
```

## Requisitos (revisa una vez)
```bash
python3 --version && node --version && ffmpeg -version | head -1 && ls "/Applications/Google Chrome.app" >/dev/null && echo OK
```
Si falta algo, dile el comando de instalación (`brew install ffmpeg`).

## Paso 1 — Preguntas
Lee `references/flujo.md` (sección Paso 1). Resume cómo entiendes el tema y haz **siempre 4 preguntas** (nivel, ángulo, ejemplo de código, duración y momentos de cara) con `AskUserQuestion`. Espera respuestas.

## Paso 2 — Borrador detallado: qué aparece cada segundo + guion de voz
Lee `references/flujo.md` (Paso 2), `references/escenas.md` y `references/voz.md`. Escribe `fuente/spec.json` y valídalo con:
```bash
python3 ~/.claude/skills/video-concepto-tech/scripts/build_video.py spec.json --plan
```
Presenta el borrador en el chat (esto sí con tiempos; tablas Seg | En pantalla | Tu voz por escena, guion corrido, momentos de cara, supuestos) y pregunta qué cambia. **Itera** hasta que diga que está aprobado. Los tiempos del borrador deben ser los de `--plan`, no inventados.

## Paso 3 — Video completo + clips + copy + guion
Solo tras la aprobación. Sigue `references/flujo.md` (Paso 3): compilar → revisar cada escena con `--still` → exportar en segundo plano → escribir `copy.txt` (`references/copy-seo.md`) → `entregar.py`. La respuesta final trae, **en texto plano**: ruta, videos con duración, el **título de portada** (también en `portada.txt` y `portada.png`; define `portada` en el spec si el título de la primera escena no sirve como portada), el **copy completo** y el **guion completo**, cada uno en su propio bloque de código (sin tablas, listo para copiar y pegar; el guion es SOLO el texto que ella dice, sin tiempos, títulos ni marcas, con una línea en blanco entre escenas, porque lo pega en el teleprompter); y los mismos copy y guion quedan como `.txt` en la carpeta.

## Si ella ya tiene el audio
`build_video.py spec.json --out fuente --audio voz.m4a` reparte las escenas por palabras; con los segundos exactos donde termina cada escena (`--cortes 9.8,24.1,…`) calza al milisegundo. Luego `export_video.mjs … --audio voz.m4a` mezcla la voz en el completo y en cada clip.

## Formato por defecto: TikTok narrado (correcciones de Carli, oct 2026)
Salvo que pida otra cosa, el video narrado es **dinámico y con poco texto**: lo que cuenta es el título, el código y el resultado.
- **Portada**: solo el título (`cover` con `solo_titulo: true`), subido y centrado (deja espacio abajo para su cara), **5 s** (`dur: 5`). Sin logo, sin línea lila, sin "parte N" en pantalla (va en el copy).
- **Títulos estilo sticker** (referencia de Carli, 14 oct 2026): Poppins 800 en mayúsculas, centrados y grandes (108 px; portada 120 px), ligeramente inclinados, con borde negro y sombra dura. Las palabras **aparecen una a una** (pop). Palabra clave en rosa (`*palabra*`), opcional amarillo (`~palabra~`). Bajo el título, una **pastilla amarilla** (`pill`) con el concepto en 2–4 palabras, que NO repite el título, y destellos rosa/amarillo a los lados.
- **Amarillo `#ffd60a`**: tercer acento de marca (solo pastilla y destellos; el rosa sigue siendo el resaltado y el violeta la estructura). **Aprobado por Carli como estándar** (junto con la tipografía Poppins 800).
- **Escenas de concepto**: título corto + código (`code_focus`) + **resultado visible** (`salida`), con el valor clave en rosa. Sin kicker lila, sin notas de texto bajo el código, sin esquemas con mucho texto (`versus`, `list`…). Si el concepto es un comando, el código es el comando y la salida es lo que imprime.
- **Terminología técnica correcta en inglés** cuando así se dice en la comunidad ("lazy imports", "frozendict", "profiler"), nunca traducciones literales ("imports perezosos").
- **Resultados reales**: verifica en la doc oficial lo que imprime el código; si lo resumes (tablas largas), dilo en los supuestos. No inventes salidas ni comandos.
- **Sin recap en pantalla** ("Lo que te llevas"): el cierre es solo la animación de marca (`outro`: CARLICODE letra por letra con brillo y un cursor que hace click en "sígueme"), ~5 s, voz solo "Sígueme para más contenido tech".
Antes de construir, pregunta lo que no esté claro (qué lleva la portada, efecto del cierre, cómo pasar esquemas a código).

## Variante: video de concepto con tu cara (60 % gráficos / 40 % ella en cámara)
Para conceptos (no código): alterna tramos `cara` y tramos `diagram`. Probado con "Kubernetes en AWS (EKS) en 70 segundos".
- **Preguntas del paso 1** extra: ángulo, cómo repartir cara/gráficos (alternado por defecto, gancho y cierre en cara), analogía + arquitectura o solo una, y cómo recibir los tramos de cara.
- **`cara`**: tramo donde ella sale en cámara. **Solo queda el título** (sin marco, sin iconos ni texto; ella monta su video encima al editar; `dur` obligatorio). Con `"marco": true` se dibuja el marco "TU CARA AQUÍ" con barra de progreso (solo si lo pide). Se marca `cara: true`.
- **`diagram`**: lienzo grande 1000×1000 que se construye elemento a elemento (`box`, `dbox`, `arrow`, `text`, `pill`, `icon`, `poly`, `wave`; `cae` hace que un elemento se caiga; `escala` lo agranda). Ver `references/escenas.md`. Sincroniza los `t` con la frase que la voz dice en ese momento y revisa con `--still`.
- **Títulos**: `==palabra==` = marcador amarillo, `*palabra*` rosa, `~palabra~` amarillo de texto; `title_px` ajusta el tamaño. El título de cada tramo se ve centrado y grande.
- **Estructura 70 s**: cara 8 → gráfico 12 → cara 6 → gráfico 14 → cara 6 → gráfico 12 → cara 6 → cierre 6 (≈63/37). La primera escena puede ser `cara` (ya no exige `cover`).
- Dibujos genéricos (cajas con nombre), no los íconos oficiales de AWS; dilo en los supuestos.

## Reglas
- El video sin audio es la **base visual**: ella graba mirándolo y lo edita (su cara va encima en las escenas marcadas `cara`).
- Exactitud técnica: si algo es simplificación, dilo en la voz y en los supuestos; no inventes cifras. Datos ilustrativos → `// datos de ejemplo`.
- Un concepto por video. Si necesita más de ~90 s, propón serie de 2 partes.
- Texto en pantalla corto (las celdas de `escenas.md` marcan los límites); código ≤12 líneas y ≤40 caracteres por línea para que se lea en el celular.
- Para editar: cambia `fuente/spec.json`, recompila y re-exporta (`--only N` re-exporta una escena y vuelve a pegar el completo).
