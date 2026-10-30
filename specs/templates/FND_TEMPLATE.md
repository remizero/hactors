<!-- schema: finding/2.0 -->

# Plantilla de hallazgo (FND-nnnnn)

[actor: human | agent] utiliza esta plantilla al registrar un hallazgo.
Lo que debe contener un hallazgo, sus mínimos, su ubicación y sus reglas de operación se definen en [FINDING.md](../FINDING.md).
Los campos vacíos son información por resolver, no hechos afirmados.

## Identidad

| Campo | Formato | Ejemplo |
|---|---|---|
| ID | `FND-nnnnn` único en el proyecto | `FND-00042` |

Un identificador retirado no se reutiliza. El hallazgo pertenece al proyecto que lo registra, con identidad única; identificar nuevos afectados no cambia su origen ni crea copias del hallazgo.

## Esquema YAML

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

## Campos

| Campo | Descripción |
|---|---|
| `id` | `FND-nnnnn`; único en el proyecto; no se reutiliza al retirar. |
| `title` | Descripción concisa del hecho observado. |
| `kind` | Tipo de hallazgo; ver tabla de tipos. |
| `severity` | Impacto; ver tabla de severidad. |
| `state` | Estado actual; ver tabla de estados. |
| `source` | Procedencia: actividad, ejecución o fuente donde se detectó el hallazgo; no enumera los afectados ni atribuye por sí sola la causa del defecto. |
| `source.execution` | Ruta completa de la ejecución de origen desde `hactors/`, relativa al proyecto, cuando exista; conserva todos sus ancestros conforme a [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md). |
| `source.artifact` | Fuente o artefacto cuya observación originó el hallazgo, cuando corresponda; no implica que ese artefacto esté afectado. |
| `source.workflow` | WORKFLOW del contexto de origen, cuando corresponda; no sustituye la identidad de su ejecución. |
| `source.task` | TASK del contexto de origen, cuando corresponda. |
| `source.rfc` | RFC del contexto de origen, cuando corresponda; no declara afectación. |
| `actions` | Lista de `AC-nnnnn`: acciones que tratan este hallazgo. |
| `relations` | Artefactos afectados mediante vínculos `affects`; ver «Relaciones de afectación». |
| `opened` | `YYYY-MM-DD` de registro. |
| `updated` | `YYYY-MM-DD` de la última modificación. |
| `resolved` | `YYYY-MM-DD` del cierre terminal; null si no está resuelto. |

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

Las consecuencias de cada estado sobre la TASK de origen se definen en [FINDING.md](../FINDING.md).

## Ubicación

El hallazgo se registra directamente en el directorio del artefacto o de la ejecución que lo originó, en un archivo `FND-nnnnn.yaml` por hallazgo.
No existe un registro central de hallazgos.

El esquema anterior muestra la entrada como elemento de lista; el archivo escrito contiene esa misma entrada sin el guion de lista, con `id` ya asignado. Las reglas de ubicación según el origen se definen en [FINDING.md](../FINDING.md).

## Registro con la CLI

`hactors create-finding` asigna el `id` y la procedencia, y acepta `--origin`, `--title`, `--kind`, `--severity`, `--opened` y `--updated`. Sin `--origin` la procedencia es la ruta de la instancia activa. Los valores declarados se registran literalmente; los campos omitidos conservan los de [finding_template.yaml](finding_template.yaml), y un valor vacío explícito sustituye al de la plantilla.

El comando no rellena `relations`, `actions` ni el resto de `source`: la afectación y el contexto documental los completa quien registra, conforme a los mínimos de [FINDING.md](../FINDING.md). Tampoco valida `kind` ni `severity` contra sus tablas, ni el formato de `opened`, `updated` o `resolved`. El origen admitido y lo que el comando no hace se describen en [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md#14-registro-de-hallazgos-desde-cualquier-origen).
