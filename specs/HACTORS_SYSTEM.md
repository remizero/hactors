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
| task_run | Unidad de ejecución dentro del workflow, asociada a una RFC específica. |
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
│   │   │   └── manifest.yaml
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
| `hactors/workflow_run_XXXXXX/task_run_XXXXXX/` | task_run | Unidad de ejecución asociada a una RFC, anidada dentro del workflow_run. |
| `projects/.state.yaml` | Estado activo | Proyecto en uso y workflow_run actual. |

### Reglas de anidamiento

- Un `task_run` siempre vive dentro de un `workflow_run`. No existe un task_run suelto fuera de un workflow.
- Un `workflow_run` siempre vive dentro de `hactors/` en el directorio del proyecto.
- Los contadores son secuenciales y con formato de seis dígitos: `workflow_run_000001`, `task_run_000042`.
- El estado activo (`.state.yaml`) es compartido por todos los proyectos; indica sobre cuál se trabaja y cuál es el workflow_run en curso.

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

Los contadores son independientes por tipo. Un proyecto puede tener `workflow_run: 3` y `task_run: 7` si el tercer workflow contiene siete task_runs en total.

### Ejemplo

Un proyecto con un workflow_run creado y dos task_runs dentro de ese workflow:

```yaml
project: "mi_proyecto"
relations: []
counters:
  task: 0
  workflow_run: 1
  task_run: 2
```

Esto indica que existe `workflow_run_000001` y, dentro de él, `task_run_000001` y `task_run_000002`.

## 4. Archivo de estado activo

El archivo `.state.yaml` mantiene el contexto de trabajo actual. Se encuentra en `projects/.state.yaml`, compartido por todos los proyectos del repositorio.

### Estructura

```yaml
active_project: ""
current_workflow_run: ""
```

### Campos

**`active_project`** — Nombre del proyecto sobre el cual operan los comandos CLI. Debe referenciar un proyecto existente en `projects/`.

**`current_workflow_run`** — ID del workflow_run activo (ej: `workflow_run_000001`). Los comandos que crean task_runs lo usan para saber dónde crear.

### Comportamiento

- **`hactors use-project <nombre>`** establece `active_project` y limpia `current_workflow_run`. Cambiar de proyecto resetea el contexto de ejecución.
- **`hactors create-workflow`** crea un nuevo workflow_run y actualiza `current_workflow_run` con su ID.
- **`hactors create-task-run`** lee ambos campos: necesita un proyecto activo y un workflow_run activo para crear el task_run en la ubicación correcta.

### Ejemplo

Estado con proyecto activo y workflow en curso:

```yaml
active_project: "mi_proyecto"
current_workflow_run: "workflow_run_000001"
```

Estado tras cambiar de proyecto:

```yaml
active_project: "otro_proyecto"
current_workflow_run: ""
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

Un `task_run` es una unidad de ejecución concreta asociada a una RFC específica. Vive dentro de un `workflow_run` y representa el trabajo necesario para cumplir los criterios de esa RFC.

### Ubicación

```
hactors/workflow_run_000001/task_run_000001/manifest.yaml
```

Cada task_run tiene su propio directorio dentro del workflow_run que lo contiene. No puede existir un task_run fuera de un workflow_run.

### Estructura y campos

La estructura del manifiesto se define en [task_run_template.yaml](templates/task_run_template.yaml). Los campos son:

**`identity.id`** — Identificador único del task_run. Coincide con el nombre del directorio.

**`identity.rfc_ref`** — Referencia a la RFC que este task_run ejecuta. Puede estar vacío si el task_run se crea antes de asociarlo a una RFC.

**`state.status`** — Estado de ejecución del task_run (ej: `pending`, `in_progress`, `blocked`, `completed`).

**`state.blocked_reason`** — Motivo del bloqueo, si el estado es `blocked`.

### Relación con workflow_run

Mientras el `workflow_run` registra el estado global del proceso (qué paso se está ejecutando, cuántos intentos se han hecho, si está bloqueado), el `task_run` registra el estado de una unidad de trabajo específica asociada a una RFC.

Un workflow_run puede contener múltiples task_runs, cada uno ejecutando una RFC diferente. Por ejemplo:

```
workflow_run_000001/
├── manifest.yaml          # estado global del workflow
├── task_run_000001/
│   └── manifest.yaml      # ejecución de RFC-001
└── task_run_000002/
    └── manifest.yaml      # ejecución de RFC-002
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

Esto establece la cadena de trazabilidad: TASK → workflow_run → task_runs → RFCs.

## 8. Cadena de trazabilidad

El sistema de ejecución HACTORS mantiene una cadena de trazabilidad completa desde la intención inicial hasta la verificación final. Cada eslabón se establece mediante referencias explícitas entre artefactos.

### La cadena

```
TASK → workflow_run → task_run → RFC
```

Cada artefacto referencia al anterior y al siguiente:

- **TASK → workflow_run**: El workflow_run tiene `task_ref` que apunta a la TASK que lo inició.
- **workflow_run → task_run**: Los task_runs viven físicamente dentro del directorio del workflow_run.
- **task_run → RFC**: El task_run tiene `rfc_ref` que apunta a la RFC que ejecuta.

### Ejemplo completo

Dada una TASK `task_000001` que ejecuta dos RFCs:

```yaml
# tasks/task_000001.md
task: "Implementar sistema de autenticación"
rfcs:
  - "RFC-001"
  - "RFC-002"
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

Dentro del workflow_run, se crean dos task_runs, uno por cada RFC:

```yaml
# hactors/workflow_run_000001/task_run_000001/manifest.yaml
identity:
  id: "task_run_000001"
  rfc_ref: "RFC-001"
state:
  status: "completed"
```

```yaml
# hactors/workflow_run_000001/task_run_000002/manifest.yaml
identity:
  id: "task_run_000002"
  rfc_ref: "RFC-002"
state:
  status: "in_progress"
```

### Reconstrucción del estado

Dado cualquier artefacto, es posible reconstruir la cadena completa:

- Desde un **task_run**, se navega al directorio padre para encontrar el **workflow_run**, y del `rfc_ref` se obtiene la **RFC**. Del `task_ref` del workflow_run se obtiene la **TASK**.
- Desde una **TASK**, se buscan en el manifest del proyecto los workflow_runs que la referencian en `task_ref`.
- Desde una **RFC**, se buscan los task_runs que la referencian en `rfc_ref`.

El manifest del proyecto (`manifest.yaml`) puede registrar estas relaciones en su campo `relations` para facilitar la navegación sin recorrer el árbol de directorios.

### Principio fundamental

La trazabilidad no es opcional. Cada artefacto debe poder responder:

- ¿Qué lo inició? (referencia al anterior)
- ¿Qué produjo? (referencia al siguiente o deliverables)
- ¿Qué evidencia lo respalda? (evidence, verification_refs)

Si un artefacto no puede responder estas preguntas, el sistema está incompleto.
