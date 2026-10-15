# carrusel-tech

Skill de Claude Code que convierte la idea de un tema tech/IA en un carrusel de Instagram animado (estilo tech: negro, rosa y violeta) y lo entrega como **un video MP4 vertical por slide (mínimo 10 s) + `copy.md` con SEO y 5 hashtags**.

Flujo: idea → propuesta de slides en texto → preguntas → construcción y revisión → exportación a MP4 → copy → verificación.

- `SKILL.md`: instrucciones del flujo.
- `scripts/`: `build_carousel.py` (spec JSON → HTML), `export_videos.mjs` (HTML → MP4), `verify_output.py`, `add_icon.sh`.
- `references/`: layouts disponibles, guía de copy/SEO, estilo de marca y un ejemplo completo.
- `assets/`: CSS/JS del carrusel e iconos Lucide (ver `assets/icons/LICENSE-lucide.txt`).

Requisitos: Python 3, Node ≥ 22, ffmpeg y Google Chrome.

Instalación: copiar esta carpeta a `~/.claude/skills/carrusel-tech/`.
