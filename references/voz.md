# Voz y guion
Si existe la skill `guion-tiktok` (`~/.claude/skills/guion-tiktok/`), antes de escribir `voz` lee su `references/estilo.md` y 1–2 transcripciones de `transcripciones/` para calcar la voz de la persona. Si no existe, usa las reglas de este archivo.
Aquí además:
- El video es **explicación de un concepto**: gancho (≤15 palabras, sin saludo) → problema → mecanismo → código → error común/remate → pregunta final.
- La voz **acompaña** lo que se ve: cada frase coincide con lo que aparece en ese segundo. No leas el código línea por línea: explica la idea ("aquí es donde se queda esperando").
- Frases de 6–14 palabras (cabe en 2–5 s), tuteo, humor ligero, explica en simple primero y el tecnicismo después.
- Cuando aparece la cara: frases más personales (gancho y cierre), sin depender de lo que hay en pantalla.
- Cierre: pregunta a la audiencia + "sígueme para más contenido tech".
- No inventes cifras; marca simplificaciones ("simplificando…").

## Narración, no etiquetas (feedback de Carli)
`voz` es lo que ella dice en voz alta: **narración fluida**, no títulos ni apuntes.
- Sin dos puntos, viñetas ni fórmulas de lista ("Primera: lazy imports."). Los dos puntos no se leen. Di "La primera es lazy imports…", "Y la quinta es…".
- Las advertencias se dicen como se hablan: "Ojo, porque solo funciona a nivel de módulo", no "Ojo: solo a nivel de módulo."
- Une las frases con conectores naturales ("así que", "y lo mejor es que", "recién se cargan cuando…") y engancha con tono de conversación ("la tercera te va a encantar").
- Símbolos dichos como suenan ("PYTHONUTF8 igual a cero").
- Tras escribirla, relee buscando `:` `;` paréntesis y guiones largos en `voz`.
- Usa el término técnico tal como se dice ("lazy imports", "frozendict", "profiler"). Si algo se dice distinto en español de uso común, ponlo así en voz y en pantalla.
- Cuando el código muestra un resultado, la voz lo nombra ("da False… y después da True") para que coincida con lo que aparece.
