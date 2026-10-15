# Flujo de 3 pasos (detalle)

## Paso 1 — Preguntas
Resume en 2–3 líneas cómo entendiste el tema y qué concepto concreto cubrirías (acótalo si es amplio). Luego **siempre** 4 preguntas con `AskUserQuestion` (marca tu recomendación primero; si el mensaje ya contestó alguna, ofrécela como recomendada):
1. **Nivel** de la audiencia (principiante / intermedio / avanzado).
2. **Ángulo**: concepto explicado desde cero · error común · "qué pasa por dentro" · comparación A vs. B.
3. **Código**: lenguaje y ejemplo (propón 2–3 ejemplos concretos y cortos, ≤12 líneas).
4. **Duración y cara**: 45 s / 60 s / 90 s, y cuándo apareces (solo gancho y cierre · también a mitad · nunca).
No construyas nada hasta tener las respuestas.

## Paso 2 — Borrador detallado (todo en el chat)
Antes de escribirlo, verifica en la doc oficial el código y sus salidas, y redacta `spec.json` (en `~/Documents/Contenido tech skill/<slug>/fuente/`) y corre `build_video.py spec.json --plan`: valida los layouts, da los tiempos reales y los segundos exactos en que aparece cada elemento. Con eso escribe el borrador:

**Cabecera**: título · palabra clave SEO (con 2 alternativas) · duración total · nº de escenas · palabras · momentos de cara.

**Por cada escena** una tabla con filas de 1–4 s (los segundos son del video completo, no de la escena):
| Seg | En pantalla | Tu voz |
|---|---|---|
| 0–3 | lo que aparece/cambia en ese tramo (usa los segundos de `--plan`) | la frase que dices en ese tramo (≈2.6 palabras/s) |
Encabezado de cada escena: `ESCENA 3 · mecanismo · 14–27 s · tipo cycle`. Marca `CARA` donde apareces.

**Guion corrido**: la voz de todo el video seguida, para leerla de una vez.
**Supuestos y exactitud**: qué es simplificación, qué datos son de ejemplo.
Cierra con: "¿Qué cambias? Cuando lo apruebes paso a generar el video."
Itera: cada cambio → edita `spec.json`, vuelve a `--plan`, muestra solo las escenas modificadas y los tiempos nuevos. No pases al paso 3 sin un "apruebo / listo / dale" claro.

## Paso 3 — Generar y entregar
1. `python3 scripts/build_video.py spec.json --out fuente` (si ya hay audio: `--audio voz.m4a` y, si tiene los cortes, `--cortes`).
2. Revisa cada escena antes de exportar: `node scripts/export_video.mjs fuente/video.html /tmp/check --still N:SEG` (SEG = un segundo con todo visible) y mira la imagen: textos cortados, solapes, vacíos.
3. Exporta en segundo plano (≈ 4–8 min): `node scripts/export_video.mjs fuente/video.html . ` desde la carpeta del video. Genera `clips/NN-id.mp4` y `video-completo.mp4`.
4. Escribe `copy.txt` (ver `copy-seo.md`).
5. `python3 scripts/entregar.py <carpeta>`: crea `guion.txt` (solo texto de la voz), verifica todo e imprime copy y guion.
6. Responde con: ruta · lista de videos con duración · **título de portada** (texto + `portada.png`) · **copy completo pegado** y **guion completo pegado, ambos en texto plano dentro de bloques de código (nunca en tabla). El guion es solo el texto de la voz (teleprompter): sin tiempos, sin títulos, sin [CARA]**. Los momentos de cara y sus tiempos se dicen aparte, en una línea fuera del bloque. · supuestos. Dile cómo usarlo: graba la voz mirando `video-completo.mp4` y súbela; si quiere, devuélveme el audio (y los segundos de corte) y re-renderizo con `--audio` para que todo calce.
