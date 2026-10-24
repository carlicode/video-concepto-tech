# Estilo Carli Code — tech oscuro (opción B: negro + rosa + violeta)

## Formato
Vertical **1080×1920**. Zonas libres para la interfaz de Instagram: ~250 px arriba y ~330 px abajo (el contenido mide 912×1000 dentro de esa franja). Todo en español.

## Paleta
| Token | Valor | Uso |
|---|---|---|
| Fondo | `#09090b` | con cuadrícula tenue y brillos rosa (arriba derecha) y violeta (abajo izquierda) |
| Panel | `#111114` | tarjetas, nodos, iconos |
| Líneas | `#26262c` | bordes, separadores |
| Texto | `#f4f4f5` | títulos y texto principal |
| Texto apagado | `#8b8b95` | apoyo, handle, notas |
| **Rosa** | `#ff4d94` | palabra clave, flechas y líneas, barras destacadas, cursor, alertas |
| **Violeta** | `#a78bfa` | iconos, comentarios `//`, nodos, umbrales, CTA |

Regla: **rosa = lo que se destaca o fluye; violeta = estructura y apoyo.** Sin verde ni otros colores; para capas secundarias, grises.

## Tipografía y tono
Space Grotesk 700 para títulos (tracking negativo) y JetBrains Mono para etiquetas, descripciones, notas y handle. Etiquetas como comentarios de código (`// el ciclo`). Iconos Lucide, nunca emojis. Minimalista: pocos elementos, mucho aire.

## Contenido
1. Portada minimalista: logo CARLI CODE pequeño arriba a la izquierda, `// tema`, título grande con una palabra en rosa y cursor parpadeante, una línea de apoyo, handle.
2. Sin números de slide.
3. Único texto de marca: `@carli.code` abajo al centro (más el logo en la portada).
4. Logo: cuadrado rosa con una "C" negra y un cursor parpadeante.
5. Última slide: checklist + CTA simple `$ sígueme para más contenido tech`.
6. Datos inventados: `// datos de ejemplo` dentro de la slide.

## Animación y video
- Portada: completa desde el primer cuadro (solo se mueve el cursor y el fondo).
- Resto: etiqueta, título y handle fijos desde el primer cuadro; el contenido se anima de arriba hacia abajo desde el segundo 0, a velocidad normal, con pausa final para leer.
- Duración mínima por slide: 10 s.
- Prohibido el SMIL (`<animate>`): no se puede capturar cuadro a cuadro. Usa animaciones CSS.
