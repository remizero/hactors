# Sistema de ejecución HACTORS.

> **Alcance de la CLI:** implementa la jerarquía recursiva, la ruta activa completa y la navegación descritas en este documento. Los comandos crean y seleccionan instancias; no generan artefactos RFC/PLAN/TEST ni gestionan su aprobación, avance o cierre.

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
| rfc_run | Instancia de ejecución de una RFC, dentro de un task_run o de un plan_run. |
| PLAN | Documento que ordena pasos y puntos de decisión derivados de una RFC y puede proponer nuevas RFCs. |
| plan_run | Instancia de ejecución de un PLAN, dentro de un rfc_run; puede contener ejecuciones de RFCs derivadas. |
| TEST | Artefacto inmutable que define una verificación, distinto de sus ejecuciones y resultados. |
| test_run | Instancia de ejecución de un TEST, dentro de un rfc_run inicial o derivado. |
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
│   │   │       ├── plan_run_000001/
│   │   │       │   ├── manifest.yaml
│   │   │       │   ├── rfc_run_000002/
│   │   │       │   │   ├── manifest.yaml
│   │   │       │   │   └── plan_run_000002/
│   │   │       │   │       ├── manifest.yaml
│   │   │       │   │       └── rfc_run_000003/
│   │   │       │   │           ├── manifest.yaml
│   │   │       │   │           └── test_run_000002/
│   │   │       │   │               └── manifest.yaml
│   │   │       │   └── rfc_run_000004/
│   │   │       │       └── manifest.yaml
│   │   │       └── test_run_000001/
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
| `…/task_run_XXXXXX/rfc_run_XXXXXX/` o `…/plan_run_XXXXXX/rfc_run_XXXXXX/` | rfc_run | Ejecución que referencia una RFC inicial o derivada. |
| `…/rfc_run_XXXXXX/plan_run_XXXXXX/` | plan_run | Ejecución que referencia un PLAN y puede contener nuevos rfc_runs. |
| `…/rfc_run_XXXXXX/test_run_XXXXXX/` | test_run | Ejecución que referencia un TEST, sin hijos de ejecución en este modelo. |
| `projects/.state.yaml` | Estado activo | Proyecto y ruta completa de la instancia seleccionada, con todos sus ancestros. |

### Reglas de anidamiento

| Padre inmediato | Hijos de ejecución permitidos |
|-----------------|--------------------------------|
| `hactors/` del proyecto | `workflow_run` |
| `workflow_run` | `task_run` |
| `task_run` | `rfc_run` |
| `rfc_run` | `plan_run`, `test_run` |
| `plan_run` | `rfc_run` |
| `test_run` | Ninguno en el modelo actual |

- Cada padre puede contener cero o varias instancias de los tipos permitidos. No toda RFC produce un PLAN o un TEST ni todo PLAN deriva nuevas RFCs; plan_runs y test_runs pueden coexistir bajo un mismo rfc_run.
- Tras `workflow_run → task_run`, las ramas recursivas alternan `rfc_run → plan_run → rfc_run → …`, sin una profundidad fija del modelo. Desde cualquier rfc_run puede abrirse una rama `rfc_run → test_run`, que termina allí. Cada ruta concreta es finita y queda sujeta a los límites del sistema de archivos.
- Cada instancia tiene un único padre inmediato y conserva su ubicación. No se reutiliza una instancia como hija de otro padre ni se enlaza un ancestro como descendiente; el árbol de cada workflow_run no contiene ciclos.
- Pueden repetirse los tipos, pero no la identidad de una instancia dentro del proyecto. Ejecutar de nuevo un documento requiere otra instancia con otro ID; el mismo documento referenciado no convierte esas instancias en una sola.
- Los IDs son secuenciales por tipo y proyecto, con un mínimo de seis dígitos. El número no codifica parentesco ni profundidad.
- El estado activo (`.state.yaml`) conserva una sola ruta seleccionada, no todo el árbol. Las demás ramas permanecen en sus directorios aunque no estén activas.

### Ascendencia y profundidad

La **profundidad de ejecución** es el número de aristas desde el workflow_run hasta la instancia: el workflow_run tiene profundidad `0`, su task_run `1` y cada hijo suma `1`. El proyecto y el directorio `hactors/` no cuentan como niveles de ejecución.

Para la rama más profunda del árbol anterior:

| Profundidad | Instancia | Padre inmediato |
|-------------|-----------|-----------------|
| 0 | `workflow_run_000001` | `hactors/` del proyecto |
| 1 | `task_run_000001` | `workflow_run_000001` |
| 2 | `rfc_run_000001` | `task_run_000001` |
| 3 | `plan_run_000001` | `rfc_run_000001` |
| 4 | `rfc_run_000002` | `plan_run_000001` |
| 5 | `plan_run_000002` | `rfc_run_000002` |
| 6 | `rfc_run_000003` | `plan_run_000002` |
| 7 | `test_run_000002` | `rfc_run_000003` |

`rfc_run_000004` es hermano de `rfc_run_000002`: ambos tienen profundidad `4`. No es descendiente de `rfc_run_000003`, aunque su número sea mayor. `test_run_000001` tiene profundidad `3`, igual que su hermano `plan_run_000001`; `test_run_000002` conserva todos los ancestros de su RFC padre y suma un nivel.

La ascendencia se reconstruye como una **secuencia ordenada de instancias**, mediante todos los prefijos de la ruta. No se reduce a un mapa por tipo ni se elimina un ancestro porque otro tenga el mismo tipo. Para `rfc_run_000003`, las RFCs ancestras son las instancias `rfc_run_000001` y `rfc_run_000002`, en sus posiciones originales; ninguna sustituye a la otra.

Padre, ascendencia y profundidad se calculan desde la ruta; no se duplican como campos persistentes en los manifiestos o en el estado activo. La profundidad documental de una RFC, definida por su derivación, es distinta de esta profundidad de ejecución.

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
| `rfc_run` | Un rfc_run dentro de un task_run o de un plan_run | `rfc_run_000001` |
| `plan_run` | Un plan_run dentro de un rfc_run | `plan_run_000001` |
| `test_run` | Un test_run dentro de un rfc_run | `test_run_000001` |

Los contadores son independientes por tipo y globales al proyecto, no al padre ni a la profundidad. En el árbol de la sección 2, los cuatro rfc_runs consumen el mismo contador aunque tengan padres y profundidades diferentes; lo mismo ocurre con los dos test_runs y su propio contador. Los contadores de ejecución no numeran artefactos RFC, PLAN ni TEST y no se reinician al abrir una rama.

Los nuevos contadores se incorporan al manifest de un proyecto existente al crear su primera instancia; no es necesario reescribir sus ejecuciones anteriores. Antes de persistir el incremento se comprueba que el ID candidato no repita un ancestro ni tenga ya una entrada en el padre elegido. Si un contador ausente o desfasado provoca uno de esos conflictos, se rechaza la creación sin modificarlo; no se renumeran instancias ni se reparan contadores automáticamente.

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
  test_run: 0
```

Los contadores registran la numeración asignada, no la ubicación ni una comprobación de existencia. El parentesco de las instancias del ejemplo se obtiene de sus directorios, no de estos valores.

## 4. Archivo de estado activo

El archivo `.state.yaml` mantiene el contexto de trabajo actual. Se encuentra en `projects/.state.yaml`, compartido por todos los proyectos del repositorio.

### Estructura

```yaml
active_project: ""
active_run_path: ""
```

### Campos y resolución

**`active_project`** — Nombre del proyecto sobre el cual operan los comandos CLI. Debe referenciar un proyecto existente en `projects/`. Si está vacío, la ruta también debe estar vacía y no hay contexto activo.

**`active_run_path`** — Ruta relativa a `projects/<active_project>/`, desde `hactors/` hasta el directorio de la instancia seleccionada, sin `manifest.yaml` ni separador final. Se almacena como una cadena con `/` entre componentes. Vacía significa que solo está seleccionado el proyecto; `hactors/` por sí solo no selecciona una instancia.

Ejemplo con tres rfc_runs y dos plan_runs en la misma ascendencia:

```yaml
active_project: "mi_proyecto"
active_run_path: "hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001/rfc_run_000002/plan_run_000002/rfc_run_000003"
```

La instancia activa es únicamente el último componente (`rfc_run_000003`). Los anteriores son sus ancestros, no selecciones independientes. Excluido `hactors/`, la ruta tiene siete componentes: su profundidad es `7 - 1 = 6`, según la convención de la sección 2. El padre se obtiene quitando un componente, sin buscar otro nodo por su tipo.

### Validación de la ruta

Antes de seleccionar una ruta o usarla como padre de una creación:

- Validar el proyecto y su manifest, y aceptar únicamente rutas relativas con el prefijo `hactors/` y componentes completos de IDs de ejecución. Rechazar rutas absolutas, componentes vacíos, `.` y `..`, separadores alternativos y rutas a archivos; no corregirlas silenciosamente.
- Validar **todos** los componentes y cada transición padre-hijo de la sección 2. No usar una lista de posiciones de longitud fija ni ignorar un sufijo desconocido.
- Verificar que cada directorio de ejecución y su `manifest.yaml` existen, y que `identity.id` coincide con su componente de ruta. Para workflow_run, comprobar además la clave envolvente de su manifiesto.
- Mantener la ruta física dentro del proyecto y rechazar enlaces simbólicos en `hactors/`, los directorios de ejecución y sus manifiestos: no deben introducir alias, saltos de ascendencia ni ciclos, incluso dentro del mismo proyecto.
- Rechazar IDs de instancia repetidos en la ruta, pero conservar todas las apariciones de un **tipo**. La unicidad global de IDs se mantiene mediante los contadores del proyecto.

Una ruta inválida o un padre incompatible produce un error sin cambiar la selección ni consumir un contador. No se recorta hasta un ancestro válido ni se elige automáticamente el último run creado. El contexto solo se actualiza después de crear correctamente la nueva instancia y su manifiesto; esto no implica una transacción general ante fallos de escritura.

### Selección y creación

| Operación | Contexto requerido | Resultado en el estado activo |
|-----------|--------------------|--------------------------------|
| `hactors use-project <nombre>` | Proyecto existente | Establece el proyecto y deja `active_run_path` vacía. |
| `hactors use-run <ruta>` | Proyecto activo y ruta completa válida relativa a ese proyecto | Selecciona la instancia indicada con toda su ascendencia, aunque pertenezca a otra rama o workflow del mismo proyecto. |
| `hactors use-run --parent` | Instancia activa válida | Quita exactamente el último componente; desde el workflow_run deja la ruta vacía y mantiene el proyecto. |
| `hactors create-workflow` | Proyecto activo | Crea un workflow_run en `hactors/` y sustituye la ruta activa por la del nuevo workflow. |
| `hactors create-task-run` | La instancia activa es un workflow_run | Crea su hijo task_run y añade el ID a la ruta activa. |
| `hactors create-rfc-run` | La instancia activa es un task_run o un plan_run | Crea su hijo rfc_run y añade el ID a la ruta activa. |
| `hactors create-plan-run` | La instancia activa es un rfc_run | Crea su hijo plan_run y añade el ID a la ruta activa. |
| `hactors create-test-run` | La instancia activa es un rfc_run | Crea su hijo test_run y añade el ID a la ruta activa. |

`use-run` acepta una ruta completa o `--parent`, mutuamente excluyentes; no acepta un ID aislado, un tipo ni una profundidad como selector. `--parent` sin instancia activa falla sin modificar el estado. Seleccionar o ascender solo cambia el contexto: no mueve directorios, no borra ramas y no cambia estados de ejecución.

Cada creación de un hijo opera sobre la **instancia seleccionada**, nunca sobre el ancestro compatible más cercano. Para crear un hermano, se selecciona primero el padre compartido; para crear varios plan_runs o test_runs de una RFC, se vuelve a ese rfc_run después de cada creación. Un test_run seleccionado no admite crear hijos; debe seleccionarse otro padre compatible. Crear un hijo preserva todos los prefijos ancestrales, aunque se repitan sus tipos. Seleccionar otra rama reemplaza la ruta activa, pero no la ascendencia almacenada físicamente en ninguna de las ramas.

Los comandos crean únicamente instancias y sus manifiestos, no los artefactos RFC/PLAN/TEST ni su aprobación. Las referencias pueden quedar vacías para asociarlas posteriormente; cuando se proporcionan, se registran sin validar el contenido del artefacto referenciado. La ruta es estructuralmente válida aun cuando falten referencias documentales, pero su trazabilidad documental queda pendiente. Crear una instancia no ejecuta su trabajo, no produce resultados ni evidencia, no autoriza la ejecución ni modifica los estados de sus ancestros.

### Secuencia CLI

Ejemplo en un proyecto con contadores de ejecución inicialmente a cero; las referencias documentales son ilustrativas:

```bash
hactors use-project mi_proyecto
hactors create-workflow --task-ref task_000001
hactors create-task-run
hactors create-rfc-run --rfc-ref RFC-A00001
hactors create-plan-run --plan-ref PLAN-00001
hactors create-rfc-run --rfc-ref RFC-A00001-F00001
hactors create-plan-run --plan-ref PLAN-00002
hactors create-rfc-run --rfc-ref RFC-A00001-F00001-T00001
```

La ruta resultante es la del ejemplo anterior, con profundidad `6`. Para crear otra RFC bajo el primer plan_run, sin confundirlo con el segundo:

```bash
hactors use-run hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001
hactors create-rfc-run --rfc-ref RFC-A00001-F00002
hactors use-run --parent
```

Se crea `rfc_run_000004` a profundidad `4`, hermano de `rfc_run_000002`. La última operación vuelve a `plan_run_000001` a profundidad `3`, desde donde puede crearse otra RFC hermana. Ninguna operación elimina la rama que alcanza `rfc_run_000003`.

Para añadir ejecuciones TEST bajo la RFC inicial y una derivada:

```bash
hactors use-run hactors/workflow_run_000001/task_run_000001/rfc_run_000001
hactors create-test-run --test-ref verificacion-autenticacion
hactors use-run --parent
hactors use-run hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001/rfc_run_000002/plan_run_000002/rfc_run_000003
hactors create-test-run --test-ref verificacion-autenticacion
```

Se crean `test_run_000001` a profundidad `3` y `test_run_000002` a profundidad `7`, como en el árbol de la sección 2. Queda seleccionada la ruta completa del segundo test_run. La referencia es ilustrativa, no una convención de nombres TEST; reutilizar un TEST compatible no reutiliza la identidad de su ejecución, conforme a [TESTS.md](TESTS.md).

Todos los comandos anteriores admiten `--root <directorio-hactors>`. `--rfc-ref` pertenece a `create-rfc-run`, no a `create-task-run`; `--plan-ref` pertenece a `create-plan-run` y `--test-ref` a `create-test-run`.

### Transición desde el formato anterior

El formato anterior conservaba `current_workflow_run`, `current_task_run` y `current_rfc_run`, sin seleccionar el plan_run al crearlo. Esos campos no representan ancestros de tipos repetidos y se sustituyen por `active_run_path`, sin mantener ambos formatos ni guardar campos adicionales de padre o profundidad.

La transición es explícita: ante un estado del formato anterior, los comandos que consumen contexto fallan sin modificarlo y piden reseleccionar el proyecto mediante `use-project` y después la instancia mediante `use-run <ruta>`. `use-project` escribe el nuevo formato; no se infiere un plan_run activo ni se busca una rama por fecha o número.

Los directorios y manifiestos existentes ya son prefijos válidos del árbol recursivo: se conservan sus IDs, contadores, referencias y ubicación, sin migrar ejecuciones ni documentos. La selección explícita puede recuperar toda su ascendencia desde la ruta.

Tras cambiar de proyecto, el estado será:

```yaml
active_project: "otro_proyecto"
active_run_path: ""
```

El archivo se crea mediante `use-project`. Si falta el contexto requerido, las operaciones fallan con un mensaje claro.

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

Un `task_run` es una unidad de trabajo dentro de un `workflow_run`. Agrupa instancias `rfc_run` iniciales, cada una asociada a una RFC específica, sin duplicar sus referencias documentales. Sus descendientes pueden alternar rfc_runs y plan_runs y contener test_runs bajo cualquier rfc_run según la sección 2; todos conservan el mismo task_run y workflow_run ancestrales.

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

Un workflow_run puede contener múltiples task_runs. Este ejemplo independiente muestra solo RFCs iniciales, sin expandir posibles descendientes:

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

Una TASK es el artefacto que inicia el proceso de ejecución. Sin una TASK asociada no se inicia la ejecución de un workflow_run; crear su estructura con `task_ref` vacío no satisface este requisito. La TASK define qué se pretende hacer, qué RFCs están involucradas, quién la ejecuta y qué criterios de aceptación debe cumplir.

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

Esto inicia la cadena de trazabilidad descrita en la sección 8. Cada nuevo rfc_run, plan_run o test_run conserva la TASK iniciadora a través de todos sus ancestros, no mediante una copia de `task_ref` en cada nivel.

## 8. Cadena de trazabilidad

El sistema de ejecución HACTORS mantiene una cadena de trazabilidad completa desde la intención inicial hasta la verificación final. Cada eslabón se establece mediante referencias explícitas entre artefactos.

### La cadena

```
TASK ← workflow_run → task_run → rfc_run → plan_run → rfc_run → plan_run → …
                                  ↓          ↓          ↓          ↓
                                 RFC        PLAN       RFC        PLAN
```

Las flechas hacia TASK, RFC y PLAN representan referencias documentales; entre instancias representan anidamiento. El diagrama muestra una rama recursiva; cada rfc_run también puede contener test_runs conforme a la sección 2:

- **workflow_run → TASK**: `task_ref` apunta a la TASK que inició la ejecución.
- **workflow_run → task_run → rfc_run → plan_run → rfc_run → …**: cada instancia vive dentro de su padre inmediato; la repetición continúa con nuevas identidades.
- **rfc_run → RFC**: `identity.rfc_ref` identifica la especificación de esa instancia, a cualquier profundidad.
- **plan_run → PLAN**: `identity.plan_ref` identifica el plan; su documento conserva el origen RFC y las decisiones, sin duplicarlos en la ejecución.
- **rfc_run → test_run → TEST**: el primer vínculo es contención; `identity.test_ref` establece el segundo sin copiar el TEST ni la referencia RFC del padre.

### Derivación documental y contención de ejecuciones

Un PLAN propone RFCs mediante `derived_rfcs`, conforme a [PLAN_TEMPLATE.md](templates/PLAN_TEMPLATE.md). Cada RFC derivada conserva su relación documental `derives` con la RFC de origen, según [RFC.md](RFC.md); el PLAN es el documento que organiza esa derivación, no un sustituto de la RFC de origen.

En la ejecución, el padre inmediato del rfc_run derivado es el **plan_run** que lo contiene; el rfc_run de origen es su abuelo. Ambos permanecen en la ruta, junto con cualquier ascendencia anterior. La contención no sustituye las relaciones documentales, no las registra automáticamente y no permite deducir aprobación o dependencias de ejecución.

### Ejemplo completo

Para el árbol recursivo de la sección 2, una TASK `task_000001` puede referenciar la RFC inicial y las derivadas involucradas:

```yaml
# tasks/task_000001.md
task: "Implementar sistema de autenticación"
rfcs:
  - "RFC-A00001"
  - "RFC-A00001-F00001"
  - "RFC-A00001-F00001-T00001"
  - "RFC-A00001-F00002"
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

Dentro del workflow_run se crea un task_run y, dentro de él, el rfc_run inicial. Si esa RFC produce `PLAN-00001`, su plan_run puede contener ejecuciones de RFCs derivadas. Estos fragmentos ilustran estados durante el trabajo, no valores asignados por los comandos de creación:

```yaml
# hactors/workflow_run_000001/task_run_000001/rfc_run_000001/manifest.yaml
identity:
  id: "rfc_run_000001"
  rfc_ref: "RFC-A00001"
state:
  status: "completed"
```

```yaml
# hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001/rfc_run_000002/manifest.yaml
identity:
  id: "rfc_run_000002"
  rfc_ref: "RFC-A00001-F00001"
state:
  status: "in_progress"
```

El `plan_run_000001` intermedio referencia `PLAN-00001` mediante `identity.plan_ref`. Si la RFC derivada produce `PLAN-00002`, su ejecución se anida en `rfc_run_000002/plan_run_000002/`; la ejecución de `RFC-A00001-F00001-T00001` será `rfc_run_000003` dentro de ese segundo plan_run. La RFC `RFC-A00001-F00002` tiene su ejecución hermana `rfc_run_000004` bajo el primer plan_run, no bajo el segundo. Las profundidades resultantes son las de la sección 2.

### Reconstrucción del estado

Dado cualquier artefacto vinculado, es posible reconstruir la cadena completa:

- Desde un **plan_run**, `plan_ref` identifica el **PLAN** y el directorio padre lleva al **rfc_run** de origen.
- Desde un **test_run**, `test_ref` identifica el **TEST** y el directorio padre lleva al **rfc_run** correspondiente; se conserva toda su ascendencia, aunque incluya otros rfc_runs.
- Desde un **rfc_run**, `rfc_ref` identifica su **RFC**. Su padre es un **task_run** si es inicial, o un **plan_run** si es derivado; en este último caso se sigue ascendiendo por todos los plan_runs y rfc_runs anteriores, sin colapsarlos por tipo.
- Desde un **task_run**, se navega al padre **workflow_run** y de su `task_ref` se obtiene la **TASK**.
- Desde una **TASK**, se buscan los workflow_runs que la referencian en `task_ref`.
- Desde una **RFC**, un **PLAN** o un **TEST**, se buscan todas sus instancias por `rfc_ref`, `plan_ref` o `test_ref`, respectivamente, recorriendo recursivamente las ramas a cualquier profundidad. Una referencia documental puede devolver varias rutas de ejecución, no una selección activa implícita.

La reconstrucción parte de la ruta de la instancia y sus manifiestos, no requiere que esa rama esté activa. Al ascender se elimina un componente cada vez; al descender se añade uno por hijo. Así se preservan la identidad de cada ancestro y su profundidad original, incluso cuando los tipos se repiten.

El manifest del proyecto (`manifest.yaml`) puede registrar relaciones documentales en `relations` para facilitar su consulta. No sustituye el árbol físico ni requiere copiar la cadena completa de ancestros o su profundidad.

### Principio fundamental

La trazabilidad no es opcional. Cada artefacto debe poder responder:

- ¿Qué lo inició? (referencia al anterior)
- ¿Qué produjo? (referencia al siguiente o deliverables)
- ¿Qué evidencia lo respalda? (evidence, verification_refs)

Si un artefacto no puede responder estas preguntas, el sistema está incompleto.

## 9. rfc_run: ejecución de una RFC

La RFC es la especificación; el `rfc_run` registra una instancia de su ejecución. Su manifiesto se define en [rfc_run_template.yaml](templates/rfc_run_template.yaml), con `identity.rfc_ref` como referencia a la RFC de esa instancia, no de toda la rama. La identidad documental y sus convenciones siguen en [RFC.md](RFC.md).

Un rfc_run inicial tiene como padre un task_run; uno derivado, un plan_run. Ambos usan la misma plantilla y el mismo contador de proyecto: no se introduce un tipo distinto por profundidad ni se copian las referencias de los rfc_runs ancestrales. Su padre y todos sus ancestros se obtienen de la ruta.

Cada rfc_run puede contener varios plan_runs y test_runs si la RFC produce planes y tests, sin restringirlo a un tipo documental de RFC. Los estados de ejecución no sustituyen el ciclo de vida ni la aprobación del documento RFC. Una nueva instancia no modifica la especificación original ni una ejecución anterior.

## 10. plan_run: ejecución de un PLAN

El PLAN define la secuencia, los criterios de avance y los puntos de decisión; el `plan_run` registra una instancia de su ejecución. La estructura del manifiesto se define en [plan_run_template.yaml](templates/plan_run_template.yaml): `identity.plan_ref` apunta al documento, mientras `state` registra el estado de la instancia y su motivo de bloqueo.

El documento PLAN conserva su contenido, origen y ciclo de vida conforme a [PLAN_TEMPLATE.md](templates/PLAN_TEMPLATE.md). El rfc_run padre proporciona el contexto de ejecución de su RFC de origen; esa referencia no se repite en plan_run. Crear el manifiesto no aprueba el plan ni supera ninguno de sus puntos de decisión.

Un plan_run puede contener cero o varios rfc_runs, correspondientes a las RFCs derivadas que se decida instanciar. Cada hijo puede producir nuevos plan_runs y continuar la jerarquía, o contener test_runs. Se crean individualmente: `derived_rfcs` no genera automáticamente documentos ni ejecuciones, y la mera contención no acredita que una RFC esté declarada en ese campo.

El modelo de contención no añade reglas de aprobación, avance o cierre automático: siguen sujetos a los documentos y decisiones correspondientes. La recursión no modifica las plantillas de manifiesto ni duplica pasos, gates o listas de hijos; estos últimos se obtienen de los directorios inmediatos.

## 11. test_run: ejecución de un TEST

El artefacto TEST y su inmutabilidad se definen en [TESTS.md](TESTS.md). El `test_run` representa una instancia independiente; su manifiesto se define en [test_run_template.yaml](templates/test_run_template.yaml). `identity.id` identifica la ejecución, `identity.test_ref` referencia el TEST y `state` registra su estado y motivo de bloqueo. Los valores iniciales proceden de la plantilla.

Su padre inmediato es un rfc_run, inicial o derivado, y no contiene otros runs en el modelo actual. La RFC de contexto se obtiene del padre, sin duplicar `rfc_ref`; la ruta conserva todos los ancestros y determina la profundidad. Un mismo TEST puede tener varias instancias con IDs distintos, bajo el mismo rfc_run o bajo otros rfc_runs cuando el escenario sea compatible.

`create-test-run` crea el directorio y su manifiesto y selecciona la nueva ruta. No genera ni modifica el artefacto TEST, no lo ejecuta y no produce resultados ni evidencia. Las reglas de evidencia se definen en [EVIDENCE.md](EVIDENCE.md); crear una instancia no acredita una verificación satisfactoria ni cierra su RFC.
