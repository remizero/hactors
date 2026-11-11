# Estado y cierre del proyecto

## Alcance

Define la jerarquía del trabajo, la propiedad de su cierre y las invariantes que hacen que un cierre sea satisfactorio.

[WORKFLOW.md](WORKFLOW.md) ordena las acciones; [LIFECYCLE.md](LIFECYCLE.md) fija los estados y sus transiciones. Las transiciones que tocan más de un archivo siguen el protocolo de [TRANSACTIONS.md](TRANSACTIONS.md).

Este documento trata del estado del trabajo, no del **estado activo**: `projects/.state.yaml` registra el contexto de selección conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#4-archivo-de-estado-activo), y ninguna selección cambia el estado de un artefacto ni autoriza una transición.

## Jerarquía

```text
WORKFLOW ─▶ TASK ─▶ RFC ─▶ Acción
```

`WORKFLOW` es el flujo que agrupa un alcance, `TASK` una unidad de trabajo que lo inicia, `RFC` una decisión contratada y `Acción` (`ACT-nnnnn`) un entregable individual bajo una RFC. Cada nivel conserva su propio estado conforme a [LIFECYCLE.md](LIFECYCLE.md).

La jerarquía es documental: ordena alcances, no ejecuciones. El árbol de instancias `workflow_run → task_run → rfc_run → …` es otra estructura, definida en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#reglas-de-anidamiento); la contención de una instancia no la incorpora a esta jerarquía ni produce una arista del grafo, conforme a [RELATIONSHIPS.md](RELATIONSHIPS.md).

Un entregable de tipo `plan` produce un documento `PLAN-nnnnn` cuyos estados pertenecen a [PLAN_TEMPLATE.md](templates/PLAN_TEMPLATE.md); el PLAN no declara acciones derivadas, así que las que su ejecución motive se declaran en el campo `actions:` de la RFC que lo produce.

## Regla de consistencia entre niveles

El cierre satisfactorio de un nivel exige el cierre satisfactorio de todo lo que está debajo. Cada nivel nombra su éxito propio: WORKFLOW `closed`, TASK `done`, RFC `done`, acción `completed`.

[actor: human | agent] mantiene estas invariantes al cerrar:

1. Un WORKFLOW pasa a `closed` solo con cada TASK de su alcance en `done`.
2. Una TASK pasa a `done` solo con cada RFC de su alcance en `done`.
3. Una RFC pasa a `done` solo con cada acción de su alcance en `completed`.
4. Un WORKFLOW puede permanecer `active` con todas sus TASK en `done`.

`rejected`, `cancelled`, `superseded` y `deprecated` no satisfacen 1–3 por sí solos. Un padre con un descendiente en uno de esos estados tiene dos salidas, y cada una es disposición `[actor: human]`:

- **Cancelar el padre**: la RFC pasa a `cancelled`, la TASK a `cancelled` y el WORKFLOW a `aborted`, preservando el trabajo y la evidencia producidos.
- **Reducir su alcance**: `[actor: human]` retira al hijo del alcance del padre con la justificación registrada en el documento del padre. El hijo conserva identidad y estado; el resto del alcance puede cerrar.

Un hijo `superseded` satisface 1–3 solo cuando `[actor: human]` incorpora su sucesor al alcance del padre —es un cambio de alcance, no una consecuencia automática— y aquel alcanza el éxito de su propio nivel, con la sustitución declarada en ambos sentidos conforme a [RELATIONSHIPS.md](RELATIONSHIPS.md#restricciones).

La segunda salida y la incorporación del sucesor exigen un alcance del padre que admita el retiro o la sustitución de forma observable: lo es el campo `rfcs:` de una TASK, y no lo es el campo `actions:` de una RFC, cuyas acciones en estado terminal conservan su entrada conforme a [Historial](#historial) y cuyo elemento no declara ni el sucesor de una acción ni un marcador de fuera de alcance, conforme a [RFC_TEMPLATE.md](templates/RFC_TEMPLATE.md#acciones-derivadas). Al nivel de la acción derivada la única salida es la primera: una RFC con una acción en `cancelled` o en `superseded` solo cierra cancelándose ella misma, que es lo que la comprobación de [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#17-transición-de-estados-documentales) refleja al exigir `completed` en cada elemento.

La regla se evalúa en el momento del cierre, no en retroactivo: un `deprecated` posterior no reabre al padre ya cerrado. Violarla bloquea la transición, y la comprobación que lo hace efectivo sobre los datos persistidos está en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#17-transición-de-estados-documentales); no se fuerza el cierre del nivel padre y ningún descendiente propaga su estado hacia arriba por sí solo.

La terminalidad tampoco consolida por sí sola el resumen, que es otra operación con su propio actor, conforme a [LIFECYCLE.md](LIFECYCLE.md#summary). Cerrar un artefacto no consolida su resumen, y consolidarlo no cierra el artefacto que resume.

## Propiedad del estado

| Nivel | Actor que puede cerrarlo | Autoridad humana requerida |
|---|---|---|
| WORKFLOW | `[actor: human]` | Sí, siempre. |
| TASK | `[actor: human]` | Sí, siempre. |
| RFC | `[actor: human \| agent]` | Aprobación de criterios y revisión. |
| Acción | `[actor: human \| agent]` | Solo cuando su tipo lo exija. |

[actor: agent] propone el cierre; [actor: human] lo autoriza en WORKFLOW y TASK. La cancelación y, en un WORKFLOW, la disposición `aborted` son también `[actor: human]`: un agente las propone, no las decide. [actor: human] reserva además la adopción de cambios de diseño, la aceptación de evidencia insuficiente, la decisión `wont-fix` de un hallazgo conforme a [FINDING.md](FINDING.md) y la consolidación de un resumen conforme a [SUMMARY.md](SUMMARY.md). Las excepciones a estas reglas siguen el mecanismo de [EXCEPTIONS.md](EXCEPTIONS.md).

## Transiciones de una acción

Los estados admitidos y sus caminos están en [ACT_TEMPLATE.md](templates/ACT_TEMPLATE.md); aquí se fija quién los recorre y qué efecto tienen.

| Transición | Actor | Condición |
|---|---|---|
| Creación en `pending` | `[actor: human \| agent]` | La acción está autorizada por la RFC y numerada con el contador `action`. |
| `pending` → `in-progress` | `[actor: human \| agent]` | Inicio del trabajo; sus `depends_on` están satisfechas. |
| `pending` ↔ `blocked` | `[actor: human \| agent]` | Una dependencia o decisión no resuelta; el motivo consta en la RFC. |
| `in-progress` → `completed` | `[actor: human \| agent]` | Entregable producido y al menos una evidencia referenciable. |
| `in-progress` → `cancelled` | `[actor: human]` | Detenida antes de completar, con motivo registrado. |
| `completed` → `superseded` | `[actor: human]` | Reemplazada por otra acción identificada. |

Una acción `completed` sin evidencia verificable incumple el requisito y bloquea la regla 3; la corrección se aplica en la acción, no rebajando la exigencia. `cancelled` y `superseded` no satisfacen la regla 3 por sí solas y activan las dos salidas de la sección anterior.

## Identificadores estables

| Nivel | Formato | Numeración |
|---|---|---|
| WORKFLOW | `WORKFLOW-nnnnn`; su versión publicada se escribe `WORKFLOW-nnnnn@vNNN`. | Contador `workflow_run` del manifest del proyecto, compartido con su ejecución: la definición se redacta con el número que tendrá su workflow_run y no lo consume. Su estado, incluida la disposición `closed`, se registra en el `status` del catálogo conforme a [templates/WORKFLOW_TEMPLATE.md](templates/WORKFLOW_TEMPLATE.md). |
| TASK | `TASK-nnnnn` | Contador `task` del manifest del proyecto. |
| RFC | Conforme a [RFC.md](RFC.md#identidad-y-tipos). | Contador `rfc_<tipo>` del manifest del proyecto, uno por tipo; la asignación sigue [RFC_SYSTEM.md](RFC_SYSTEM.md#numeración). |
| Acción | `ACT-nnnnn` | Contador `action` del manifest del proyecto. |

Los contadores y su alcance están en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#contadores). Un identificador retirado no se reutiliza, y el número no codifica parentesco, profundidad ni orden temporal.

## Relaciones y evidencia

Toda relación que un nivel declare se representa en el grafo del proyecto conforme a [RELATIONSHIPS.md](RELATIONSHIPS.md). Una acción pasa a `completed` solo con al menos una evidencia referenciable vinculada a su RFC y a la revisión examinada, cuyo formato mínimo está en [EVIDENCE.md](EVIDENCE.md).

Una revisión de Git es un metadato complementario de integración, nunca el mecanismo de reconstrucción del estado, conforme a [LIFECYCLE.md](LIFECYCLE.md#flujo-de-integración).

## Historial

- Las RFC cerradas permanecen en `rfcs/`: son historia técnica verificable. No hay índice ni archivo que las traslade, y ninguna consulta de estado las recorre a mano: la responden las vistas generadas conforme a [VIEWS.md](VIEWS.md).
- Las acciones en estado terminal conservan su entrada en el campo `actions:` de su RFC; no se eliminan.
- Los workflow_run cerrados conservan su directorio y sus manifiestos, incluidos sus intentos fallidos; no se borran ni se reescriben.
- Ni un resumen ni una vista reconstruyen el estado: lo sintetizan o lo proyectan desde los artefactos, conforme a [SUMMARY.md](SUMMARY.md#reconstrucción) y a [VIEWS.md](VIEWS.md).

## Carga de estado

[actor: human | agent] al incorporarse a un nivel:

1. Lee el documento del nivel: la TASK, la RFC y su campo `actions:`.
2. Localiza sus ejecuciones por el árbol de instancias, desde la ruta activa o desde la referencia documental, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#reconstrucción-del-estado).
3. Consulta las vistas generadas para una lectura agregada, sin tratarlas como fuente.
4. Lee los hallazgos `FND-nnnnn.yaml` registrados junto a los orígenes de su alcance, conforme a [FINDING.md](FINDING.md).

No cargar directorios ajenos al alcance de la TASK vigente. La política de lectura de normas es [CONTEXT_LOADING.md](CONTEXT_LOADING.md); esta sección no la sustituye ni la amplía.
