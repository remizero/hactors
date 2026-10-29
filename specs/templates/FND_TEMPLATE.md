<!-- schema: finding/2.0 -->

# Plantilla de hallazgo (FND-nnnnn)

[actor: human | agent] utiliza esta plantilla al registrar un hallazgo en `findings.yaml` dentro del proyecto.
El formato, los campos, las relaciones de afectación y las reglas de operación se definen aquí.
Los campos vacíos son información por resolver, no hechos afirmados.

## Qué es un hallazgo

Un hallazgo afirma un hecho observado: defecto, brecha, inconsistencia, riesgo o ausencia verificada.
No aprueba cambios ni reemplaza una RFC; puede derivar en una o quedar como antecedente documentado.
Pertenece al proyecto que lo registra, con identidad única; identificar nuevos afectados no cambia su origen ni crea copias del hallazgo.

## Esquema YAML

Copiar como entrada en `findings.yaml` del proyecto.

```yaml
- id: FND-00001
  title: ""
  kind: ""
  severity: ""
  state: open
  source:
    execution: ""
    artifact: ""
    workflow: ""
    task: ""
    rfc: ""
  actions: []
  relations: []
  opened: ""
  updated: ""
  resolved: null
```

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | `FND-nnnnn` | Identificador único en el proyecto; no se reutiliza al retirar. |
| `title` | texto | Descripción concisa del hecho observado. |
| `kind` | enum | Tipo de hallazgo; ver tabla de tipos. |
| `severity` | enum | Impacto; ver tabla de severidad. |
| `state` | enum | Estado actual; ver tabla de estados. |
| `source` | objeto | Procedencia: actividad, ejecución o fuente donde se detectó el hallazgo; no enumera los afectados ni atribuye por sí sola la causa del defecto. |
| `source.execution` | ruta | Ruta completa de la ejecución de origen desde `hactors/`, relativa al proyecto, cuando exista; conserva todos sus ancestros conforme a [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md). |
| `source.artifact` | ruta | Fuente o artefacto cuya observación originó el hallazgo, cuando corresponda; no implica que ese artefacto esté afectado. |
| `source.workflow` | referencia | WORKFLOW del contexto de origen, cuando corresponda; no sustituye la identidad de su ejecución. |
| `source.task` | referencia | TASK del contexto de origen, cuando corresponda. |
| `source.rfc` | referencia | RFC del contexto de origen, cuando corresponda; no declara afectación. |
| `actions` | lista de `AC-nnnnn` | Acciones que tratan este hallazgo. |
| `relations` | lista de relaciones | Artefactos afectados mediante vínculos `affects`; ver «Relaciones de afectación». |
| `opened` | `YYYY-MM-DD` | Fecha de registro. |
| `updated` | `YYYY-MM-DD` | Última modificación. |
| `resolved` | `YYYY-MM-DD` o null | Fecha de cierre terminal; null si no resuelto. |

Omitir las referencias documentales de `source` que ya puedan recuperarse de `source.execution` y sus manifiestos; no copiar la ascendencia en campos por tipo. Si no existe una ejecución, identificar la fuente y el contexto documental disponible sin inventar un run.

## Relaciones de afectación

Cada entrada de `relations` contiene `target` y `relation`; la dirección es **este FND → artefacto afectado**. `relation: affects` declara un impacto observado sobre el destino, que puede ser una RFC, un TEST, un HARNESS u otro artefacto identificable. Para un criterio u objetivo local, incluir la referencia al artefacto que lo define.

El origen y los afectados son independientes: detectar un defecto durante un TEST no significa que el TEST sea defectuoso. El artefacto de origen también puede estar afectado, pero debe declararse explícitamente; ya no se excluye por ser fuente. Cada afectación debe justificarse con lo observado, no deducirse de la procedencia o la ubicación.

Fragmento ilustrativo de un hallazgo detectado en un test_run de una RFC derivada que afecta a varias RFCs y a un HARNESS; las referencias deben resolverse y justificarse en el proyecto.

```yaml
source:
  execution: "hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001/rfc_run_000002/test_run_000001"
relations:
  - target: "RFC-A00001"
    relation: affects
  - target: "RFC-F00002"
    relation: affects
  - target: "HRN-00001"
    relation: affects
```

Los afectados se declaran únicamente en `relations`: no mantener una lista `affects` paralela ni usar `source` para enumerarlos. Añadir afectados no altera el origen ni resuelve el hallazgo automáticamente.

Las evidencias que sustentan el hallazgo lo referencian mediante `supports`, conforme a [EVD_TEMPLATE.md](EVD_TEMPLATE.md); esa relación de respaldo no se confunde con la procedencia ni con `affects`.

## Tipos

| `kind` | Uso |
|---|---|
| `defect` | Comportamiento incorrecto observado. |
| `gap` | Requisito sin cubierta, contrato sin implementación. |
| `inconsistency` | Fuentes o comportamientos que discrepan. |
| `risk` | Amenaza probable sin ocurrencia actual. |
| `blocker` | Impide avanzar hasta una resolución externa. |
| `observation` | Nota relevante sin acción inmediata. |

## Severidad

| Valor | Criterio |
|---|---|
| `critical` | Detiene el WORKFLOW o expone un requisito de seguridad no cubierto. |
| `high` | Bloquea una TASK o invalida un criterio aprobado. |
| `medium` | Degrada la calidad sin impedir el avance de la TASK. |
| `low` | Detalle utilizable pero mejorable. |
| `info` | Contexto sin consecuencia práctica. |

## Estados y transiciones

| Estado | Significado |
|---|---|
| `open` | Registrado, sin acción asociada. |
| `tracked` | Una o más acciones lo tratan. |
| `resolved` | Acción completada y evidencia verificada. |
| `wont-fix` | Se decide no actuar, con motivo y autoridad humana. |
| `superseded` | Sustituido por otro hallazgo. |

```text
open → tracked → resolved
open → wont-fix
open → superseded
tracked → open   (si se retira la acción)
```

Un `critical` o `high` en estado `open` bloquea el cierre de la TASK donde se originó.

## Operación

| Acción | Actor |
|---|---|
| Registrar un hallazgo detectado. | `[actor: human \| agent]` |
| Clasificar severidad inicial. | `[actor: human \| agent]` |
| Cambiar `open` a `tracked`. | `[actor: human \| agent]` |
| Marcar `resolved`. | `[actor: human \| agent]` con evidencia. |
| Decidir `wont-fix`. | `[actor: human]`. |
| Modificar severidad tras análisis. | `[actor: human]` si afecta alcance aprobado. |

## Relación con RFC y TASK

El contexto de origen se obtiene de `source`, no de la lista de afectados. La TASK de origen se recupera siguiendo `source.execution` hasta el workflow_run y su `identity.task_ref`; cuando exista una TASK de origen que no pueda recuperarse allí, se declara en `source.task`. Las relaciones `affects` no sustituyen esa TASK ni cambian la regla de bloqueo de cierre.
Si la resolución cambia un contrato vigente, se crea la RFC correspondiente; el hallazgo queda como antecedente referenciado por `supersedes` o `informs`.
Hallazgos que impactan varios artefactos se mantienen centralizados en el `findings.yaml` del proyecto; los artefactos afectados solo los referencian por `id`.
