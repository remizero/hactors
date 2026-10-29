# Sistema de ejecución HACTORS.

## 1. ¿Qué es el sistema de ejecución HACTORS?

El sistema de ejecución HACTORS es el conjunto de artefactos, reglas y mecanismos que permiten llevar una RFC desde su intención inicial hasta su verificación final, manteniendo trazabilidad completa en cada etapa.

Una RFC define *qué* se debe hacer y *qué* criterios deben cumplirse. El sistema de ejecución define *cómo* se organiza ese trabajo, *quién* lo realiza, *en qué estado* se encuentra y *qué evidencia* lo respalda.

Este sistema se basa en tres principios:

1. **Toda ejecución nace de una TASK.** Una TASK es el artefacto que inicia el proceso. Sin TASK no hay ejecución.
2. **Toda ejecución es una instancia concreta.** No se ejecuta un workflow abstracto; se ejecuta un `workflow_run` específico, con identidad propia, estado observable y resultados registrables.
3. **Toda ejecución deja evidencia verificable.** Cada paso, cada intento y cada resultado se registra de forma que el estado del proyecto pueda reconstruirse sin depender de memoria externa.

### Artefactos que intervienen

| Artefacto | Rol en la ejecución |
|-----------|---------------------|
| TASK | Inicia el proceso. Define qué se pretende hacer y qué RFCs están involucradas. |
| workflow_run | Instancia concreta de ejecución. Contiene el estado global, los pasos y los intentos. |
| task_run | Unidad de trabajo dentro del workflow que contiene ejecuciones de RFC. |
| rfc_run | Instancia de ejecución de una RFC, dentro de un task_run. |
| PLAN | Documento que ordena pasos y puntos de decisión derivados de una RFC. |
| plan_run | Instancia de ejecución de un PLAN, dentro de un rfc_run. |
| EVIDENCE | Registros verificables que respaldan las afirmaciones de cada paso. |

### Relación entre WORKFLOW y workflow_run

Un WORKFLOW define las fases y pasos abstractos de un proceso. Un `workflow_run` es una instancia concreta de ese workflow: tiene identidad propia, un estado observable en cada momento y resultados que se preservan.

La distinción es importante: el WORKFLOW dice *cómo debería ser* el proceso; el `workflow_run` registra *cómo fue* la ejecución real, incluyendo intentos fallidos, bloqueos y decisiones tomadas durante el recorrido.

## 2. Estructura de directorios de ejecución

La ejecución se organiza físicamente dentro del directorio del proyecto. Cada artefacto tiene una ubicación propia y anidada:

```
projects/<project_name>/
├── hactors/
│   ├── workflow_run_000001/
│   │   ├── manifest.yaml
│   │   ├── task_run_000001/
│   │   │   ├── manifest.yaml
│   │   │   └── rfc_run_000001/
│   │   │       ├── manifest.yaml
│   │   │       └── plan_run_000001/
│   │   │           └── manifest.yaml
│   │   └── task_run_000002/
│   │       └── manifest.yaml
│   └── workflow_run_000002/
│       └── manifest.yaml
├── rfcs/
├── standards/
├── tasks/
├── manifest.yaml
└── project.yaml
```

Adicionalmente, el archivo de estado activo se encuentra en:

```
projects/.state.yaml
```

### Qué representa cada elemento

| Ruta | Artefacto | Contenido |
|------|-----------|-----------|
| `project.yaml` | Identidad del proyecto | Nombre, descripción, fecha de creación y referencia normativa. |
| `manifest.yaml` | Grafo del proyecto | Relaciones entre artefactos y contadores de ejecución. |
| `tasks/` | TASKs | Artefactos iniciadores. Cada TASK define qué se pretende ejecutar. |
| `rfcs/` | RFCs | Especificaciones normativas originales e inmutables. |
| `standards/` | Normas del proyecto | Convenciones de documentación, Git y estilo de código. |
| `hactors/workflow_run_XXXXXX/` | workflow_run | Instancia de ejecución con su propio manifest. |
| `hactors/workflow_run_XXXXXX/task_run_XXXXXX/` | task_run | Unidad de trabajo que contiene ejecuciones de RFC. |
| `…/task_run_XXXXXX/rfc_run_XXXXXX/` | rfc_run | Ejecución que referencia una RFC. |
| `…/rfc_run_XXXXXX/plan_run_XXXXXX/` | plan_run | Ejecución que referencia un PLAN derivado de esa RFC. |
| `projects/.state.yaml` | Estado activo | Proyecto, workflow_run, task_run y rfc_run en uso. |

### Reglas de anidamiento

- Un `task_run` siempre vive dentro de un `workflow_run`. No existe un task_run suelto fuera de un workflow.
- Un `workflow_run` siempre vive dentro de `hactors/` en el directorio del proyecto.
- Un `rfc_run` siempre vive dentro de un `task_run`; un `plan_run`, dentro de un `rfc_run`.
- Cada padre puede contener varias instancias del nivel siguiente. No toda RFC produce un PLAN.
- Los contadores son secuenciales y con un mínimo de seis dígitos: `workflow_run_000001`, `rfc_run_000042`, `plan_run_000003`.
- El estado activo (`.state.yaml`) es compartido por todos los proyectos; conserva la cadena de contexto necesaria para crear el siguiente nivel.

## 3. Manifest del proyecto: contadores y relaciones

El archivo `manifest.yaml` en la raíz del proyecto tiene tres responsabilidades: identificar el proyecto, registrar las relaciones entre artefactos y mantener los contadores de ejecución.

### Estructura y campos

La estructura del manifest se define en [manifest_template.yaml](templates/manifest_template.yaml). Los campos son:

**`project`** — Nombre del proyecto. Debe coincidir con el nombre del directorio que lo contiene.

**`relations`** — Lista de relaciones entre artefactos. Cada relación registra una conexión identificable: qué artefacto se vincula con cuál, qué tipo de vínculo existe y dónde se encuentra físicamente. Este grafo permite navegar la trazabilidad sin mantener índices duplicados.

**`counters`** — Contadores secuenciales para cada tipo de artefacto ejecutable. Se incrementan automáticamente al crear una nueva instancia.

### Contadores

| Contador | Se incrementa al crear | Formato del ID generado |
|----------|------------------------|--------------------------|
| `task` | Una TASK en `tasks/` | `task_000001` |
| `workflow_run` | Un workflow_run en `hactors/` | `workflow_run_000001` |
| `task_run` | Un task_run dentro de un workflow_run | `task_run_000001` |
| `rfc_run` | Un rfc_run dentro de un task_run | `rfc_run_000001` |
| `plan_run` | Un plan_run dentro de un rfc_run | `plan_run_000001` |

Los contadores son independientes por tipo y globales al proyecto, no al padre. Un proyecto puede tener `workflow_run: 3` y `task_run: 7` si se han creado siete task_runs entre sus tres workflows. Los contadores de ejecución no numeran documentos RFC ni PLAN.

Los nuevos contadores se incorporan al manifest de un proyecto existente al crear su primera instancia; no es necesario reescribir sus ejecuciones anteriores.

### Ejemplo

Un proyecto con un workflow_run creado y dos task_runs dentro de ese workflow:

```yaml
project: "mi_proyecto"
relations: []
counters:
  task: 0
  workflow_run: 1
  task_run: 2
  rfc_run: 0
  plan_run: 0
```

Esto indica que existe `workflow_run_000001` y, dentro de él, `task_run_000001` y `task_run_000002`.

## 4. Archivo de estado activo

El archivo `.state.yaml` mantiene el contexto de trabajo actual. Se encuentra en `projects/.state.yaml`, compartido por todos los proyectos del repositorio.

### Estructura

```yaml
active_project: ""
current_workflow_run: ""
current_task_run: ""
current_rfc_run: ""
```

### Campos

**`active_project`** — Nombre del proyecto sobre el cual operan los comandos CLI. Debe referenciar un proyecto existente en `projects/`.

**`current_workflow_run`** — ID del workflow_run activo, dentro del proyecto.

**`current_task_run`** — ID del task_run activo, dentro de ese workflow_run.

**`current_rfc_run`** — ID del rfc_run activo, dentro de ese task_run. Determina dónde se crea un plan_run.

### Comportamiento

- **`hactors use-project <nombre>`** establece `active_project` y limpia todos los niveles de ejecución.
- **`hactors create-workflow`** establece `current_workflow_run` y limpia task_run y rfc_run activos.
- **`hactors create-task-run`** requiere proyecto y workflow activos; establece `current_task_run` y limpia `current_rfc_run`.
- **`hactors create-rfc-run`** requiere proyecto, workflow y task activos; establece `current_rfc_run`.
- **`hactors create-plan-run`** requiere la cadena activa completa y no cambia el contexto. Permite crear varios planes bajo la misma ejecución de RFC.

Los comandos crean únicamente instancias y sus manifiestos, no los documentos RFC/PLAN ni su aprobación. Las referencias pueden quedar vacías para asociarlas posteriormente; cuando se proporcionan, se registran sin validar el contenido del documento referenciado. Crear una instancia no autoriza a ejecutar su trabajo.

### Secuencia CLI

```bash
hactors use-project mi_proyecto
hactors create-workflow --task-ref task_000001
hactors create-task-run
hactors create-rfc-run --rfc-ref RFC-A00001
hactors create-plan-run --plan-ref PLAN-00001
```

Todos estos comandos admiten `--root <directorio-hactors>`. `--rfc-ref` pertenece a `create-rfc-run`, no a `create-task-run`; los registros anteriores no se migran automáticamente.

### Ejemplo

Estado con proyecto activo y workflow en curso:

```yaml
active_project: "mi_proyecto"
current_workflow_run: "workflow_run_000001"
current_task_run: "task_run_000001"
current_rfc_run: "rfc_run_000001"
```

Estado tras cambiar de proyecto:

```yaml
active_project: "otro_proyecto"
current_workflow_run: ""
current_task_run: ""
current_rfc_run: ""
```

El archivo se crea automáticamente la primera vez que se ejecuta `use-project`. Si no existe, los comandos que lo requieren fallan con un mensaje claro.

## 5. workflow_run: manifiesto de ejecución

El manifiesto de un `workflow_run` es el registro completo de una instancia de ejecución. Contiene cuatro bloques estructurales y se almacena envuelto bajo su propio ID.

### Estructura general

La estructura del manifiesto se define en [workflow_run_manifest_template.yaml](templates/workflow_run_manifest_template.yaml). El archivo `manifest.yaml` dentro de `hactors/workflow_run_XXXXXX/` se almacena envuelto bajo su propio ID:

```yaml
workflow_run_000001:
  identity:
    ...
  global_state:
    ...
  integration:
    ...
  review:
    ...
```

La clave de nivel superior es el ID del workflow_run. Todo el contenido del manifiesto vive dentro de esa clave.

### Bloque 1: identity

```yaml
identity:
  id: "workflow_run_000001"
  task_ref: "task_000001"
  workflow_version: "1.0"
```

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador único del workflow_run. Coincide con el nombre del directorio y la clave envolvente. |
| `task_ref` | Referencia a la TASK que inició esta ejecución. Puede estar vacío si el workflow_run se crea antes de asociarlo a una TASK. |
| `workflow_version` | Versión del WORKFLOW abstracto que se está ejecutando. |

### Bloque 2: global_state

```yaml
global_state:
  status: "in_progress"
  current_step: "step_002"
  blocked_reason: ""
  steps:
    step_001:
      status: "completed"
      checkpoint_ref: ""
      attempts:
        - id: attempt_001
          status: failed
          started_at: "2026-10-22T10:00:00Z"
          finished_at: "2026-10-22T10:01:00Z"
        - id: attempt_002
          status: completed
          started_at: "2026-10-22T10:05:00Z"
          finished_at: "2026-10-22T10:06:00Z"
    step_002:
      status: "in_progress"
      checkpoint_ref: ""
      attempts: []
```

| Campo | Descripción |
|-------|-------------|
| `status` | Estado general del workflow_run (ej: `pending`, `in_progress`, `blocked`, `completed`). |
| `current_step` | Paso en el que se encuentra la ejecución. |
| `blocked_reason` | Motivo del bloqueo, si el estado es `blocked`. |
| `steps` | Mapa de pasos ejecutados. Cada paso tiene su propio estado, referencia a checkpoint y lista de intentos. |

**Intentos (attempts):** Cada paso registra una lista de intentos. Un intento es una ejecución concreta de ese paso. Preserva su identidad (`attempt_001`, `attempt_002`), su resultado (`failed`, `completed`) y sus marcas de tiempo. Los intentos no se borran ni se modifican; se añaden. Esto garantiza la inmutabilidad del registro.

### Bloque 3: integration

```yaml
integration:
  git_ref: "abc1234"
  verification_refs:
    - "evidence_001"
    - "test_report_001"
```

| Campo | Descripción |
|-------|-------------|
| `git_ref` | Referencia Git (commit, tag o branch) donde se integró el resultado. |
| `verification_refs` | Referencias a evidencia de verificación (tests, reports, etc.). |

### Bloque 4: review

```yaml
review:
  acceptance: "approved"
  accepted_by: "reviewer_name"
  accepted_at: "2026-10-22T12:00:00Z"
```

| Campo | Descripción |
|-------|-------------|
| `acceptance` | Resultado de la revisión (ej: `approved`, `rejected`, `pending`). |
| `accepted_by` | Identificador de quien realizó la aceptación. |
| `accepted_at` | Marca de tiempo de la aceptación. |

## 6. task_run: unidad de ejecución dentro del workflow

Un `task_run` es una unidad de trabajo dentro de un `workflow_run`. Agrupa instancias `rfc_run`, cada una asociada a una RFC específica, sin duplicar sus referencias documentales.

### Ubicación

```
hactors/workflow_run_000001/task_run_000001/manifest.yaml
```

Cada task_run tiene su propio directorio dentro del workflow_run que lo contiene. No puede existir un task_run fuera de un workflow_run.

### Estructura y campos

La estructura del manifiesto se define en [task_run_template.yaml](templates/task_run_template.yaml). Los campos son:

**`identity.id`** — Identificador único del task_run. Coincide con el nombre del directorio. La referencia a cada RFC pertenece a su `rfc_run`, no al task_run.

**`state.status`** — Estado de ejecución del task_run (ej: `pending`, `in_progress`, `blocked`, `completed`).

**`state.blocked_reason`** — Motivo del bloqueo, si el estado es `blocked`.

### Relación con workflow_run

Mientras el `workflow_run` registra el estado global del proceso (qué paso se está ejecutando, cuántos intentos se han hecho, si está bloqueado), el `task_run` registra el estado de una unidad de trabajo que puede contener varias ejecuciones de RFC.

Un workflow_run puede contener múltiples task_runs. Por ejemplo:

```
workflow_run_000001/
├── manifest.yaml
├── task_run_000001/
│   ├── manifest.yaml
│   ├── rfc_run_000001/
│   │   └── manifest.yaml
│   └── rfc_run_000002/
│       └── manifest.yaml
└── task_run_000002/
    └── manifest.yaml
```

### Contador

Los task_runs se numeran de forma independiente por proyecto, no por workflow_run. Si un proyecto tiene dos workflow_runs, cada uno con tres task_runs, el contador del proyecto será `task_run: 6`.

## 7. TASK: artefacto iniciador

Una TASK es el artefacto que inicia el proceso de ejecución. Sin TASK no hay workflow_run. La TASK define qué se pretende hacer, qué RFCs están involucradas, quién la ejecuta y qué criterios de aceptación debe cumplir.

### Ubicación y formato

Las TASKs se almacenan en el directorio `tasks/` del proyecto, en formato Markdown con frontmatter YAML:

```
tasks/task_000001.md
```

### Estructura y reglas

La estructura completa de una TASK, sus campos y las reglas de cumplimentación se definen en [TASK_TEMPLATE.md](templates/TASK_TEMPLATE.md). Referirse a la plantilla como fuente de verdad.

### Relación con workflow_run

La TASK es el punto de partida. Cuando se crea un workflow_run, se referencia la TASK que lo inicia mediante el campo `task_ref` en el bloque `identity` del manifiesto del workflow_run:

```yaml
workflow_run_000001:
  identity:
    id: "workflow_run_000001"
    task_ref: "task_000001"
```

Esto inicia la cadena de trazabilidad: TASK → workflow_run → task_run → rfc_run → plan_run. Los dos últimos niveles referencian los documentos RFC y PLAN, respectivamente.

## 8. Cadena de trazabilidad

El sistema de ejecución HACTORS mantiene una cadena de trazabilidad completa desde la intención inicial hasta la verificación final. Cada eslabón se establece mediante referencias explícitas entre artefactos.

### La cadena

```
TASK ← workflow_run → task_run → rfc_run → plan_run
                                  ↓          ↓
                                 RFC        PLAN
```

Las flechas hacia TASK, RFC y PLAN representan referencias documentales; entre instancias representan anidamiento:

- **workflow_run → TASK**: `task_ref` apunta a la TASK que inició la ejecución.
- **workflow_run → task_run → rfc_run → plan_run**: cada instancia vive dentro de su padre.
- **rfc_run → RFC**: `identity.rfc_ref` identifica la especificación que se ejecuta.
- **plan_run → PLAN**: `identity.plan_ref` identifica el plan; su documento conserva el origen RFC y las decisiones, sin duplicarlos en la ejecución.

### Ejemplo completo

Dada una TASK `task_000001` que ejecuta dos RFCs:

```yaml
# tasks/task_000001.md
task: "Implementar sistema de autenticación"
rfcs:
  - "RFC-A00001"
  - "RFC-F00001"
actor: "human"
```

Se crea un workflow_run que referencia esa TASK:

```yaml
# hactors/workflow_run_000001/manifest.yaml
workflow_run_000001:
  identity:
    id: "workflow_run_000001"
    task_ref: "task_000001"
  global_state:
    status: "in_progress"
    current_step: "step_001"
```

Dentro del workflow_run se crea un task_run y, dentro de él, dos rfc_runs. Estos fragmentos ilustran su estado durante el trabajo, no valores asignados por los comandos de creación:

```yaml
# hactors/workflow_run_000001/task_run_000001/rfc_run_000001/manifest.yaml
identity:
  id: "rfc_run_000001"
  rfc_ref: "RFC-A00001"
state:
  status: "completed"
```

```yaml
# hactors/workflow_run_000001/task_run_000001/rfc_run_000002/manifest.yaml
identity:
  id: "rfc_run_000002"
  rfc_ref: "RFC-F00001"
state:
  status: "in_progress"
```

Si la primera RFC produce `PLAN-00001`, su ejecución vive en `rfc_run_000001/plan_run_000001/` y lo referencia mediante `identity.plan_ref`.

### Reconstrucción del estado

Dado cualquier artefacto vinculado, es posible reconstruir la cadena completa:

- Desde un **plan_run**, `plan_ref` identifica el **PLAN** y el directorio padre lleva al **rfc_run**.
- Desde un **rfc_run**, `rfc_ref` identifica la **RFC** y su padre lleva al **task_run**.
- Desde un **task_run**, se navega al padre **workflow_run** y de su `task_ref` se obtiene la **TASK**.
- Desde una **TASK**, se buscan los workflow_runs que la referencian en `task_ref`.
- Desde una **RFC**, se buscan los rfc_runs que la referencian en `rfc_ref`; desde un **PLAN**, los plan_runs que lo referencian en `plan_ref`.

El manifest del proyecto (`manifest.yaml`) puede registrar estas relaciones en su campo `relations` para facilitar la navegación sin recorrer el árbol de directorios.

### Principio fundamental

La trazabilidad no es opcional. Cada artefacto debe poder responder:

- ¿Qué lo inició? (referencia al anterior)
- ¿Qué produjo? (referencia al siguiente o deliverables)
- ¿Qué evidencia lo respalda? (evidence, verification_refs)

Si un artefacto no puede responder estas preguntas, el sistema está incompleto.

## 9. rfc_run: ejecución de una RFC

La RFC es la especificación; el `rfc_run` registra una instancia de su ejecución. Su manifiesto se define en [rfc_run_template.yaml](templates/rfc_run_template.yaml), con `identity.rfc_ref` como única referencia a la RFC dentro de la cadena de ejecución. La identidad documental y sus convenciones siguen en [RFC.md](RFC.md).

Cada rfc_run puede contener varios plan_runs si la RFC produce planes. Los estados de ejecución no sustituyen el ciclo de vida ni la aprobación del documento RFC. Una nueva instancia no modifica la especificación original ni una ejecución anterior.

## 10. plan_run: ejecución de un PLAN

El PLAN define la secuencia, los criterios de avance y los puntos de decisión; el `plan_run` registra una instancia de su ejecución. La estructura del manifiesto se define en [plan_run_template.yaml](templates/plan_run_template.yaml): `identity.plan_ref` apunta al documento, mientras `state` registra el estado de la instancia y su motivo de bloqueo.

El documento PLAN conserva su contenido, origen y ciclo de vida conforme a [PLAN_TEMPLATE.md](templates/PLAN_TEMPLATE.md). El rfc_run padre proporciona el contexto de ejecución de su RFC de origen; esa referencia no se repite en plan_run. Crear el manifiesto no aprueba el plan ni supera ninguno de sus puntos de decisión.
