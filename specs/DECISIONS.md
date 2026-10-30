# Registro de decisiones

## Alcance

Establece cuándo registrar una decisión y cómo relacionar ADR y RFC sin duplicar su contenido.
Las definiciones están en GLOSSARY.md y la autoridad documental en [ARTIFACTS.md](ARTIFACTS.md).

## Cuándo registrar

[actor: human | agent] debe documentar una decisión que:

- Introduzca o cambie límites arquitectónicos o contratos públicos.
- Seleccione una biblioteca, estructura de datos o formato binario frente a alternativas relevantes.
- Establezca un estándar, restricción o excepción técnica.
- Resuelva un compromiso significativo entre seguridad, rendimiento, complejidad y mantenimiento.

[actor: human] conserva la aprobación de esas decisiones según [LIFECYCLE.md](LIFECYCLE.md).
La necesidad de documentar una decisión no autoriza al ejecutor a adoptarla unilateralmente.

## RFC y ADR

- Si la decisión forma parte de una RFC, sus alternativas, resultado y consecuencias se registran allí.
- No crear un ADR adicional para copiar esa decisión.
- Si la decisión canónica ya está en un ADR, una RFC que la aplique lo referencia y describe únicamente el cambio propuesto.
- Si cambia la decisión, registrar su sucesora y la relación de sustitución; no mantener dos versiones vigentes contradictorias.
- La documentación actual del sistema incorpora el contrato resultante y enlaza a su justificación histórica.

## Plan y decisión secuencial

Un plan (`PLAN-nnnnn`) es una decisión secuencial: compromete un orden de ejecución, recursos y criterios de avance.
Su formato está en [templates/PLAN_TEMPLATE.md](templates/PLAN_TEMPLATE.md).
Los puntos de decisión dentro del plan (decision gates) son aprobados por [actor: human] antes de avanzar.
Si la decisión es única y no secuencial, pertenece al registro de ADR; si es un conjunto ordenado de pasos con gates, pertenece al plan.

## Contenido mínimo de un ADR

| Campo o sección | Contenido |
|---|---|
| Identidad y título | Identificador estable y descripción breve. |
| Estado y fecha | Situación de la decisión y fecha del registro. |
| Contexto | Problema, restricciones y criterios que motivan decidir. |
| Alternativas | Opciones consideradas y compromisos relevantes. |
| Decisión | Opción elegida y justificación. |
| Consecuencias | Beneficios, costes y mitigaciones. |
| Trazabilidad | RFC relacionadas, fuentes afectadas y decisión sustituta, si existe. |

## Estados de ADR

Estos estados pertenecen al registro de una decisión, no representan progreso de implementación:

| Estado | Significado |
|---|---|
| `proposed` | Alternativa documentada aún sin aprobación. |
| `accepted` | Decisión aprobada. |
| `rejected` | Alternativa descartada. |
| `superseded` | Decisión aceptada sustituida por otra identificada. |

[actor: human | agent] puede redactar una propuesta.
[actor: human] decide `proposed` → `accepted` o `rejected`, y `accepted` → `superseded`.
La sustitución debe enlazar las decisiones en ambos sentidos.

## Identidad y ubicación

Un ADR se identifica como `ADR-nnnnn`, con cinco cifras y ceros iniciales; el identificador es único en el proyecto y no se reutiliza al retirar la decisión. Cada decisión vive en su propio archivo `decisions/ADR-nnnnn — nombre-descriptivo.md` del proyecto, sin acumularse en un registro agregado, conforme a la estructura de [PROJECTS.md](PROJECTS.md). La numeración la lleva el contador `adr` del manifest del proyecto, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#contadores).

[actor: human | agent] actualiza las referencias afectadas al registrar o sustituir una decisión.
