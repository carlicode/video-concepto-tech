---
name: carrusel-tech
description: Crea carruseles/Reels de Instagram sobre tecnología e IA para Carli Code (@carli.code) en estilo tech minimalista (negro, rosa y violeta). La persona da la idea de un tema; la skill propone en texto la explicación de cada slide, hace preguntas, y con las respuestas genera los slides animados y los exporta como un video MP4 vertical por slide (mínimo 10 s cada uno), junto con el copy de la descripción con SEO y 5 hashtags. Úsala siempre que el usuario pida un carrusel, post, reel, slides o videos para Instagram sobre un tema tech o de IA, diga "hazme un carrusel de…", "quiero un post sobre…", "slides de…", o mencione su estilo de carruseles, aunque no nombre la skill.
---

# Carrusel tech para Instagram (Carli Code)

Convierte una idea de tema en un paquete listo para publicar: **un video MP4 por slide + el copy con SEO y 5 hashtags**. El flujo tiene un punto de control antes de gastar tiempo en renderizar: primero se acuerda el contenido (propuesta y preguntas) y solo después se construye.

Todo sale en español, con el estilo de marca ya definido (ver `references/style.md`). Los esquemas y gráficos son lo que distingue este formato: úsalos para explicar, no solo texto en pantalla.

## Requisitos (revisa una vez)
`python3`, `node` ≥ 22, `ffmpeg` y Google Chrome. Comprueba con:
```bash
python3 --version && node --version && ffmpeg -version | head -1 && ls "/Applications/Google Chrome.app" >/dev/null && echo OK
```
Si falta algo, díselo al usuario con el comando para instalarlo (`brew install ffmpeg`) antes de seguir.

## Flujo

### 1. Entender la idea
El usuario da un tema (puede ser una frase). Si ya incluye audiencia, ángulo o datos, úsalos y no los vuelvas a preguntar. Si el tema es ambiguo o muy amplio, acótalo tú en la propuesta en vez de interrogar.

### 2. Proponer la explicación de los slides (en el chat, antes de construir)
Escribe el esquema en texto, de 6 a 8 slides. Para cada slide:
- **Título** (corto, con la palabra clave en *asteriscos* si va en rosa).
- **Mensaje**: qué entiende la persona al verlo, en una frase.
- **Visual**: qué layout usarías y por qué (ciclo, capas, flujo, triángulo, barras, código, versus, lista). Mira `references/layouts.md`: allí están los tipos, qué cuenta mejor cada uno y sus límites.
- **Datos o ejemplos** que mostrará.

Estructura que funciona: portada → problema o idea central → 3 o 4 slides que explican con un esquema distinto cada una → resumen en lista (checklist) que termina con el CTA. No repitas el mismo layout dos veces seguidas. Cuida la exactitud técnica: si algo es una simplificación, dilo; no inventes estadísticas.

### 3. Hacer preguntas (obligatorio antes de crear cada carrusel)
Justo después de la propuesta, haz **siempre 3 o 4 preguntas**, en cada carrusel nuevo, aunque el tema parezca claro: la persona quiere decidir el enfoque antes de que se gaste tiempo en construir, y cada tema pide un nivel, un ángulo y unos datos distintos. Usa `AskUserQuestion` si está disponible; si no, pregunta en el chat con opciones numeradas y marca tu recomendación. Preguntas que cambian de verdad el resultado:
- **Audiencia y nivel** (principiante, intermedio, avanzado): define profundidad y vocabulario.
- **Ángulo**: explicar un concepto, guía paso a paso, comparación, errores comunes.
- **Datos**: ¿tienes cifras o ejemplos reales, o uso ejemplos ilustrativos marcados como tal?
- **Palabra clave de SEO** o enfoque de la publicación (propón 2 o 3 opciones).
Si el usuario ya dio alguna respuesta en su mensaje, ofrécela como opción recomendada para que la confirme en vez de saltarte la pregunta. No construyas nada hasta tener las respuestas; ajusta la propuesta según lo que digan.

### 4. Construir
1. **Carpeta de trabajo:** `~/Desktop/<slug-del-tema>/` (o la que el usuario indique). Dentro, `fuente/` para el spec y el HTML.
2. **Spec JSON** en `fuente/spec.json` siguiendo `references/layouts.md` (hay un ejemplo completo en `references/example-evaluacion.json`). La primera slide es `cover` y la última `list` (checklist + CTA `$ sígueme para más contenido tech`).
3. **Compilar:**
   ```bash
   python3 <skill>/scripts/build_carousel.py fuente/spec.json --out fuente
   ```
   Imprime la duración de cada slide (mínimo 10 s: fin de la animación + 3 s de pausa). Si dice "Icono … no existe", elige uno parecido de los sugeridos o descarga uno con `scripts/add_icon.sh <nombre>`.
4. **Revisar cada slide antes de exportar.** Genera una imagen del estado final de cada slide y mírala:
   ```bash
   node <skill>/scripts/export_videos.mjs fuente/carousel.html /tmp/check --still <N>:<segundo>
   ```
   (usa un segundo posterior al fin de la animación, p. ej. 11). Busca textos cortados o superpuestos, etiquetas que no caben, mensajes poco claros y vacíos grandes. Corrige el spec y recompila. Dedica a esto el esfuerzo: es mucho más barato que re-exportar.
5. **Exportar los videos** (tarda ~3 a 5 min; córrelo en segundo plano y espera):
   ```bash
   node <skill>/scripts/export_videos.mjs fuente/carousel.html . 
   ```
   Genera `slide-1-cover.mp4`, `slide-2-….mp4`… en 1080×1920, 30 fps. La portada sale sin animación de entrada y en las demás slides el título está fijo desde el primer cuadro; solo se anima el contenido, de arriba hacia abajo.

### 5. Escribir el copy (obligatorio en cada carrusel)
Todo carrusel se entrega con su propio `copy.md`; sin copy la entrega no está completa (el verificador lo marca como error). Si el usuario pide re-exportar o editar un carrusel viejo, revisa que tenga su `copy.md` y créalo si falta.

Sigue `references/copy-seo.md`: gancho con la palabra clave en la primera línea (≤ 125 caracteres), desarrollo breve, interacción, CTA "Sígueme para más contenido tech" y **exactamente 5 hashtags en la última línea**. Guárdalo en `copy.md` en la carpeta.

### 6. Verificar y entregar
```bash
python3 <skill>/scripts/verify_output.py <carpeta>
```
Comprueba que hay un MP4 por slide de 1080×1920 y ≥ 10 s, que existe `copy.md` y que termina con 5 hashtags. Si algo falla, corrígelo.

Antes de cerrar, confirma que la carpeta incluye **los videos y el `copy.md`**: la entrega no está completa sin el copy. Cierra con un resumen corto: ruta de la carpeta, lista de videos con su duración, el copy pegado en el chat (para copiarlo directo) y los supuestos que hiciste (p. ej. "los valores del gráfico son de ejemplo"). Ofrece ajustes concretos: cambiar un slide, otro orden o más datos.

## Estructura de la entrega
```
<slug>/
├── slide-1-cover.mp4 … slide-N-list.mp4   (un video por slide, ≥ 10 s)
├── copy.md                                (descripción con SEO + 5 hashtags)
└── fuente/ spec.json, carousel.html, meta.json   (para editar y re-exportar)
```
`carousel.html` se abre en el navegador (flechas para navegar, espacio para pausar); es la vista previa interactiva.

## Reglas de marca que no se negocian
Están detalladas en `references/style.md`; las esenciales: sin números de slide, el único texto de marca es `@carli.code` abajo al centro, una sola palabra clave en rosa por título, iconos Lucide (nunca emojis), y el CTA final simple. Los datos inventados se marcan como "datos de ejemplo". La razón de ser de estas reglas es que todos los carruseles se vean como una misma serie reconocible, minimalista y limpia.

## Editar un carrusel existente
Cambia `fuente/spec.json`, recompila y re-exporta solo lo necesario. Para re-exportar una única slide, usa `--still` para validarla y luego exporta todo (los videos de cada slide son independientes; sobrescribe los que cambiaron).
