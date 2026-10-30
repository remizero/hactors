# Resumen.

Un resumen (SUMMARY) es la síntesis del resultado de un artefacto: qué se pretendía, qué se alcanzó, qué lo respalda y qué queda pendiente.

Un resumen sintetiza; no vuelve a explicar los artefactos que referencia, no copia su contenido y no los sustituye. Cada afirmación debe poder rastrearse hasta la fuente que la respalda.

## Las siete preguntas.

Un resumen responde, como mínimo:

1. ¿Qué pretendía conseguir el artefacto resumido?
2. ¿Qué objetivos se alcanzaron?
3. ¿Qué decisiones se adoptaron?
4. ¿Qué resultados se obtuvieron?
5. ¿Qué evidencias respaldan esos resultados?
6. ¿Qué limitaciones o cuestiones quedaron pendientes?
7. ¿Cuál es el estado final que puede justificarse?

Responderlas no autoriza a reexplicar las fuentes: el resumen enuncia el resultado y remite al artefacto que lo acredita.

## Mínimos de un resumen.

1. Identificarse por el artefacto que resume; no tiene identidad ni contador propios.
2. Ser un único archivo por artefacto resumido, que evoluciona con él y declara su fase.
3. Sintetizar sin duplicar: lo que ya está en otra fuente se referencia, no se reproduce.
4. Referenciar el archivo contenedor real de cada artefacto, con la versión concreta utilizada cuando esté versionado.
5. Listar solo lo que justifica un resultado afirmado; no es un inventario del proyecto.
6. Declarar su estado final distinguiendo lo demostrado de lo pendiente.
7. No declarar cerrado lo que las comprobaciones no demostraron.

## Niveles.

Existen dos niveles, y solo dos. Las instancias intermedias —`task_run`, `rfc_run`, `plan_run`, `test_run` y `harness_run`— no tienen resumen propio: lo registrado en ellas se agrega al resumen de la RFC correspondiente o al resumen global.

| Nivel | Artefacto resumido | Ubicación |
|---|---|---|
| 1 | Una RFC | `rfcs/<nombre-sin-extension> - Summary.md`, junto a la RFC |
| 2 | Un workflow_run | `hactors/workflow_run_XXXXXX/SUMMARY.md`, junto a su manifiesto |

`hactors create-summary` crea ese archivo con su cabecera: `--origin <ruta>` declara la RFC en `rfcs/` o el workflow_run en `hactors/` y, si se omite, el destino es el workflow_run de la instancia activa. Las reglas del origen admitido y de los valores que no rellena se describen en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#15-creación-del-archivo-de-resumen).

### Nivel 1 — por RFC.

Sintetiza el resultado de esa RFC considerando exclusivamente sus objetivos, decisiones, evidencias y hallazgos relacionados. Cada RFC mantiene su autonomía documental.

Su nombre físico y la exención de RFC-D se rigen por [RFC.md](RFC.md#resumen-y-registro); el momento de su consolidación, por [RFC.md](RFC.md#resumen-post-cierre). La documentación de una RFC-D es por sí misma el resumen verificable.

Una RFC derivada tiene su propio resumen autónomo. La RFC de origen la menciona únicamente como relación `derives`, sin incorporar sus resultados; solo el resumen global los ve juntos.

### Nivel 2 — por workflow_run.

Sintetiza el resultado de toda la ejecución: las RFC, TASK, TEST, HARNESS, evidencias y hallazgos que participaron realmente. No enumera todos los artefactos ni se convierte en un segundo inventario del proyecto; se organiza en tres dimensiones:

1. **Estado**: qué objetivos y artefactos terminaron, cuáles permanecen pendientes y cuáles están bloqueados.
2. **Resultados**: qué se consiguió, qué se descubrió y qué conclusiones están respaldadas.
3. **Trazabilidad**: referencias directas a los artefactos que justifican cada resultado.

El resumen global no redefine lo que ya registra el [manifiesto del workflow_run](templates/workflow_run_manifest_template.yaml):

- El objetivo se sintetiza con sus palabras y enlaza la TASK declarada en `identity.task_ref`; los criterios de aceptación se listan con su estado.
- `global_state.status` se reproduce tal como está; el manifiesto manda y el resumen no lo reinterpreta.
- `review.acceptance`, `review.accepted_by` y `review.accepted_at` se reproducen: aceptar el flujo y consolidar el resumen son el mismo acto de [actor: human].

## Historial de ejecuciones.

El resumen de una RFC cubre todas las instancias que la ejecutan, no solo la última: su `rfc_run` y todos los descendientes, incluidos los `test_run` y `harness_run` anidados bajo un `plan_run`.

Si una RFC se ejecuta dos veces existen dos instancias distintas. Cada una conserva su propio contexto en el historial del resumen: motivo de la ejecución, estado inicial conocido, trabajo realizado, artefactos involucrados, evidencias y hallazgos producidos, resultado de la ejecución y estado final alcanzado.

Las ejecuciones siguientes no sustituyen a las anteriores, aunque se inicien para resolver un hallazgo de aquella.

## Fase y consolidación.

El resumen es un único archivo que evoluciona con el artefacto resumido y declara su fase en `status`: `in-progress` mientras se construye y `consolidated` cuando queda fijado. Sus transiciones y actores se definen en [LIFECYCLE.md](LIFECYCLE.md#summary). En `in-progress` recoge los objetivos alcanzados, las decisiones, los resultados parciales y las cuestiones pendientes, y representa una síntesis del estado conocido hasta ese momento. `consolidated` se produce cuando el artefacto alcanza su condición de finalización e integra los resultados definitivos, los objetivos cumplidos, las desviaciones, las limitaciones y las conclusiones respaldadas.

[actor: human] siempre declara la consolidación; [actor: agent] modifica el resumen por instrucción de [actor: human]. Un hallazgo `critical` o `high` en estado `open` bloquea el estado final del resumen igual que bloquea el cierre de la TASK donde se originó, conforme a [FINDING.md](FINDING.md).

Un resumen consolidado queda inmutable. Solo puede reabrirse si otra TASK del mismo workflow_run se ejecuta, y la reapertura agrega registros o resúmenes nuevos. Un registro ya consolidado no se reabre; si aun así debe cambiar, se reabre toda la línea de acceso al artefacto de ese registro.

## Estado final.

El estado final de una RFC usa los identificadores de [LIFECYCLE.md](LIFECYCLE.md) igual que `execution.status` de una TASK: es un hecho observado, no el resultado deseado, y el objetivo se expresa por separado como en `target_status`. Los criterios de aceptación se listan con su estado, distinguiendo los satisfechos de los pendientes.

El estado final de un workflow_run reproduce `global_state.status` de su manifiesto, cuyo vocabulario es el de la instancia y no el documental, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#bloque-2-global_state).

## Referencias y trazabilidad.

- Cada referencia apunta al archivo contenedor real del artefacto, con una ruta relativa al proyecto. Las evidencias y los hallazgos viven junto a su origen, así que no hay un directorio central que enlazar: se referencia el archivo concreto.
- Un artefacto versionado se referencia con la versión concreta utilizada —`HRN-00001@v002`, conforme a [HARNESS.md](HARNESS.md)—, no con la más reciente.
- Una RFC se referencia con su identidad completa, incluidos sus segmentos de derivación y su modificador.
- Un TEST se referencia por su archivo, no por su `test_run`.
- La trazabilidad se materializa de dos formas complementarias: en línea, sobre cada resultado afirmado, y como matriz de objetivo, criterio, evidencia y estado.
- Las listas no son exhaustivas: contienen lo que justifica un resultado afirmado.

## Reconstrucción.

El resumen no es fuente de verdad del estado: este se acredita a partir de los artefactos persistidos, sus estados, sus historiales y sus relaciones, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#reconstrucción-del-estado). El resumen responde a qué estado puede justificarse con lo que sobrevivió, no a cuál fue la última revisión.

Las referencias a revisiones de Git son metadatos complementarios de integración: opcionales, útiles cuando están disponibles y no duplicadas en el resumen, que las obtiene del manifiesto del workflow_run. Un hash de contenido se registra solo cuando debe verificarse la integridad o la identidad de un contenido concreto.

## Esquema.

El formato, la cabecera y las secciones se definen en [templates/SUMMARY_TEMPLATE.md](templates/SUMMARY_TEMPLATE.md).

## Operación.

| Acción | Actor |
|---|---|
| Redactar y actualizar el resumen en `in-progress`. | `[actor: human \| agent]` |
| Declarar `consolidated`. | `[actor: human]` |
| Reproducir el estado y la aceptación del manifiesto. | `[actor: human \| agent]` |
| Reabrir un resumen `consolidated`. | `[actor: human]` |
| Agregar registros o resúmenes tras la reapertura. | `[actor: human \| agent]` |

## Consultas mínimas.

[actor: human | agent] debe poder responder a partir del resumen:

- ¿Qué se pretendía y qué se alcanzó realmente?
- ¿Qué evidencia respalda cada resultado afirmado?
- ¿Qué limitaciones o cuestiones quedan pendientes y qué las bloquea?
- ¿Qué estado final puede justificarse?
- ¿Qué ejecuciones históricas produjeron ese estado?
