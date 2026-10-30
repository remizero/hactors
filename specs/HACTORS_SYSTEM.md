# Sistema de ejecución HACTORS.

> **Alcance de la CLI:** implementa la jerarquía recursiva, la ruta activa completa y la navegación descritas en este documento. Los comandos crean y seleccionan instancias; no generan artefactos RFC/PLAN/TEST/HARNESS ni gestionan su aprobación, avance o cierre. `create-harness-run` registra referencias declaradas: no resuelve catálogos, verifica contenido, publica versiones ni construye o ejecuta recetas.

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
| test_run | Instancia de ejecución de un TEST, dentro de un rfc_run inicial o derivado; puede contener harness_runs. |
| HARNESS | Receta con identidad estable y versiones publicadas inmutables; reglas en [HARNESS.md](HARNESS.md). |
| harness_run | Instancia de uso de una versión de HARNESS bajo el test_run solicitante; crearla no ejecuta ni valida la receta. |
| EVIDENCE | Registros verificables que respaldan las afirmaciones de cada paso. |

### Relación entre WORKFLOW y workflow_run

Un WORKFLOW define las fases y pasos abstractos de un proceso. Un `workflow_run` es una instancia concreta de ese workflow: tiene identidad propia, un estado observable en cada momento y resultados que se preservan.

La distinción es importante: el WORKFLOW dice *cómo debería ser* el proceso; el `workflow_run` registra *cómo fue* la ejecución real, incluyendo intentos fallidos, bloqueos y decisiones tomadas durante el recorrido.

## 2. Estructura de directorios de ejecución

La ejecución se organiza físicamente dentro del directorio del proyecto. Cada instancia tiene una ubicación propia y anidada; los catálogos y versiones de HARNESS se almacenan separadamente conforme a [HARNESS.md](HARNESS.md):

```
projects/<project_name>/
├── hactors/
│   ├── workflow_run_000001/
│   │   ├── manifest.yaml
│   │   ├── SUMMARY.md
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
│   │   │       │   │               ├── manifest.yaml
│   │   │       │   │               └── harness_run_000003/
│   │   │       │   │                   └── manifest.yaml
│   │   │       │   └── rfc_run_000004/
│   │   │       │       └── manifest.yaml
│   │   │       └── test_run_000001/
│   │   │           ├── manifest.yaml
│   │   │           ├── harness_run_000001/
│   │   │           │   ├── manifest.yaml
│   │   │           │   ├── EVD-00001.yaml
│   │   │           │   └── FND-00001.yaml
│   │   │           └── harness_run_000002/
│   │   │               └── manifest.yaml
│   │   └── task_run_000002/
│   │       └── manifest.yaml
│   └── workflow_run_000002/
│       └── manifest.yaml
├── decisions/
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
| `decisions/` | ADRs | Decisiones registradas del proyecto, cada una en su propio archivo; ver [DECISIONS.md](DECISIONS.md). |
| `tasks/` | TASKs | Artefactos iniciadores. Cada TASK define qué se pretende ejecutar. |
| `rfcs/` | RFCs | Especificaciones normativas originales e inmutables. |
| `standards/` | Normas del proyecto | Convenciones de documentación, Git y estilo de código. |
| `hactors/workflow_run_XXXXXX/` | workflow_run | Instancia de ejecución con su propio manifest. |
| `hactors/workflow_run_XXXXXX/task_run_XXXXXX/` | task_run | Unidad de trabajo que contiene ejecuciones de RFC. |
| `…/task_run_XXXXXX/rfc_run_XXXXXX/` o `…/plan_run_XXXXXX/rfc_run_XXXXXX/` | rfc_run | Ejecución que referencia una RFC inicial o derivada. |
| `…/rfc_run_XXXXXX/plan_run_XXXXXX/` | plan_run | Ejecución que referencia un PLAN y puede contener nuevos rfc_runs. |
| `…/rfc_run_XXXXXX/test_run_XXXXXX/` | test_run | Ejecución que referencia un TEST y puede contener harness_runs. |
| `…/test_run_XXXXXX/harness_run_XXXXXX/` | harness_run | Uso de una versión de HARNESS; hoja de ejecución. |
| `EVD-nnnnn.yaml` junto a su origen | EVIDENCE | Registro verificable escrito en el directorio del artefacto o ejecución que lo originó; ver sección 13. |
| `FND-nnnnn.yaml` junto a su origen | FINDING | Hecho observado escrito en el directorio del artefacto o ejecución que lo originó, con su procedencia y sus afectados; ver sección 14. |
| `SUMMARY.md` junto al manifiesto del workflow_run | SUMMARY | Síntesis del resultado de toda la ejecución; las instancias intermedias no tienen resumen propio. Ver [SUMMARY.md](SUMMARY.md). |
| `projects/.state.yaml` | Estado activo | Proyecto y ruta completa de la instancia seleccionada, con todos sus ancestros. |

### Reglas de anidamiento

| Padre inmediato | Hijos de ejecución permitidos |
|-----------------|--------------------------------|
| `hactors/` del proyecto | `workflow_run` |
| `workflow_run` | `task_run` |
| `task_run` | `rfc_run` |
| `rfc_run` | `plan_run`, `test_run` |
| `plan_run` | `rfc_run` |
| `test_run` | `harness_run` |
| `harness_run` | Ninguno |

- Cada padre puede contener cero o varias instancias de los tipos permitidos. No toda RFC produce un PLAN o un TEST ni todo PLAN deriva nuevas RFCs; plan_runs y test_runs pueden coexistir bajo un mismo rfc_run. Un TEST no necesita usar un HARNESS, pero puede contener varios usos concretos.
- Tras `workflow_run → task_run`, las ramas recursivas alternan `rfc_run → plan_run → rfc_run → …`, sin una profundidad fija del modelo. Desde cualquier rfc_run puede abrirse una rama `rfc_run → test_run → harness_run`, que termina en el HARNESS. Cada ruta concreta es finita y queda sujeta a los límites del sistema de archivos.
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
| 8 | `harness_run_000003` | `test_run_000002` |

`rfc_run_000004` es hermano de `rfc_run_000002`: ambos tienen profundidad `4`. No es descendiente de `rfc_run_000003`, aunque su número sea mayor. `test_run_000001` tiene profundidad `3`, igual que su hermano `plan_run_000001`; `test_run_000002` conserva todos los ancestros de su RFC padre y suma un nivel. Sus harness_runs añaden otro nivel: `harness_run_000001` y `harness_run_000002` tienen profundidad `4`; `harness_run_000003`, profundidad `8`.

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
| `task` | Una TASK en `tasks/` | `TASK-00001` |
| `workflow_run` | Un workflow_run en `hactors/` | `workflow_run_000001` |
| `task_run` | Un task_run dentro de un workflow_run | `task_run_000001` |
| `rfc_run` | Un rfc_run dentro de un task_run o de un plan_run | `rfc_run_000001` |
| `plan_run` | Un plan_run dentro de un rfc_run | `plan_run_000001` |
| `test_run` | Un test_run dentro de un rfc_run | `test_run_000001` |
| `harness_run` | Un harness_run dentro de un test_run | `harness_run_000001` |
| `evidence` | Una evidencia en el directorio de su origen | `EVD-00001` |
| `finding` | Un hallazgo en el directorio de su origen | `FND-00001` |
| `adr` | Una decisión en `decisions/` | `ADR-00001` |

Los contadores son independientes por tipo y globales al proyecto, no al padre ni a la profundidad. En el árbol de la sección 2, los cuatro rfc_runs consumen el mismo contador aunque tengan padres y profundidades diferentes; lo mismo ocurre con los dos test_runs y los tres harness_runs, cada tipo con su contador. Los contadores de ejecución no numeran artefactos RFC, PLAN, TEST, HRN ni versiones de receta y no se reinician al abrir una rama.

Los contadores `evidence` y `finding` no son de ejecución: numeran registros EVD y FND cuya ubicación depende de su origen, conforme a las secciones 13 y 14, por lo que un mismo proyecto los reparte entre varios directorios sin reiniciar la numeración. Los contadores `task` y `adr` tampoco lo son: numeran artefactos documentales, no instancias; el primero las TASK de `tasks/`, conforme a la sección 7, y el segundo las decisiones de `decisions/`, conforme a [DECISIONS.md](DECISIONS.md).

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
  harness_run: 0
  evidence: 0
  finding: 0
  adr: 0
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
| `hactors create-task` | Proyecto activo y su directorio `tasks/` | No cambia el estado activo: escribe `tasks/TASK-nnnnn.md` con el contador `task`. |
| `hactors create-workflow` | Proyecto activo | Crea un workflow_run en `hactors/` y sustituye la ruta activa por la del nuevo workflow. |
| `hactors create-task-run` | La instancia activa es un workflow_run | Crea su hijo task_run y añade el ID a la ruta activa. |
| `hactors create-rfc-run` | La instancia activa es un task_run o un plan_run | Crea su hijo rfc_run y añade el ID a la ruta activa. |
| `hactors create-plan-run` | La instancia activa es un rfc_run | Crea su hijo plan_run y añade el ID a la ruta activa. |
| `hactors create-test-run` | La instancia activa es un rfc_run | Crea su hijo test_run y añade el ID a la ruta activa. |
| `hactors create-harness-run` | La instancia activa es un test_run | Crea su hijo harness_run y añade el ID a la ruta activa. |
| `hactors create-evidence [--origin <ruta>]` | Proyecto activo y origen existente en ese proyecto; si `--origin` se omite, instancia activa | No cambia el estado activo: escribe `EVD-nnnnn.yaml` en el directorio del origen. |
| `hactors create-finding [--origin <ruta>]` | Proyecto activo y origen existente en ese proyecto; si `--origin` se omite, instancia activa | No cambia el estado activo: escribe `FND-nnnnn.yaml` en el directorio del origen. |
| `hactors create-summary [--origin <ruta>]` | Proyecto activo y origen existente en ese proyecto: una RFC en `rfcs/` o un workflow_run; si `--origin` se omite, el workflow_run de la instancia activa | No cambia el estado activo: escribe el archivo de resumen junto al artefacto resumido. |

`use-run` acepta una ruta completa o `--parent`, mutuamente excluyentes; no acepta un ID aislado, un tipo ni una profundidad como selector. `--parent` sin instancia activa falla sin modificar el estado. Seleccionar o ascender solo cambia el contexto: no mueve directorios, no borra ramas y no cambia estados de ejecución.

Cada creación de un hijo opera sobre la **instancia seleccionada**, nunca sobre el ancestro compatible más cercano. Para crear un hermano, se selecciona primero el padre compartido; para crear varios plan_runs o test_runs de una RFC, se vuelve a ese rfc_run después de cada creación; para varios harness_runs, se vuelve al test_run solicitante. Un harness_run seleccionado no admite crear hijos. Crear un hijo preserva todos los prefijos ancestrales, aunque se repitan sus tipos. Seleccionar otra rama reemplaza la ruta activa, pero no la ascendencia almacenada físicamente en ninguna de las ramas.

Los comandos crean únicamente instancias y sus manifiestos, no los artefactos RFC/PLAN/TEST/HARNESS ni su aprobación. Las referencias pueden quedar vacías para asociarlas posteriormente; cuando se proporcionan, se registran sin validar el contenido del artefacto referenciado. La única excepción es `--task-ref`, cuya forma escrita se normaliza al identificador de la TASK conforme a la sección 7. La ruta es estructuralmente válida aun cuando falten referencias documentales, pero su trazabilidad documental queda pendiente. Crear una instancia no ejecuta su trabajo, no produce resultados ni evidencia, no autoriza la ejecución ni modifica los estados de sus ancestros. La TASK iniciadora, la evidencia, los hallazgos y los resúmenes se crean aparte, con los comandos de las secciones 7, 13, 14 y 15.

### Secuencia CLI

Ejemplo en un proyecto con sus contadores inicialmente a cero; las referencias documentales son ilustrativas:

```bash
hactors use-project mi_proyecto
hactors create-task --task "Cerrar el alcance de autenticación"
hactors create-workflow --task-ref TASK-00001
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

Para crear usos de una receta bajo ambos TESTs, preservando el contexto solicitante:

```bash
hactors use-run hactors/workflow_run_000001/task_run_000001/rfc_run_000001/test_run_000001
hactors create-harness-run --harness-ref HRN-00001@v002
hactors use-run --parent
hactors create-harness-run --harness-ref HRN-00001@v002
hactors use-run hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001/rfc_run_000002/plan_run_000002/rfc_run_000003/test_run_000002
hactors create-harness-run --harness-ref HRN-00001@v002
```

Se crean `harness_run_000001` y `harness_run_000002` a profundidad `4`, y `harness_run_000003` a profundidad `8`; queda seleccionado el tercero. La referencia HRN es ilustrativa y declarada, no resuelta ni verificada. `content_ref`, revisión examinada y parámetros conservan los valores de la plantilla; este ejemplo no satisface los requisitos para ejecutar la receta.

Todos los comandos anteriores admiten `--root <directorio-hactors>`. `--rfc-ref` pertenece a `create-rfc-run`, no a `create-task-run`; `--plan-ref` pertenece a `create-plan-run`, `--test-ref` a `create-test-run`, y `--harness-ref` / `--content-ref` a `create-harness-run`.

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
  task_ref: "TASK-00001"
  workflow_version: "1.0"
```

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador único del workflow_run. Coincide con el nombre del directorio y la clave envolvente. |
| `task_ref` | Identificador de la TASK que inició esta ejecución, conforme a la sección 7. Puede estar vacío si el workflow_run se crea antes de asociarlo a una TASK. |
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

Un `task_run` es una unidad de trabajo dentro de un `workflow_run`. Agrupa instancias `rfc_run` iniciales, cada una asociada a una RFC específica, sin duplicar sus referencias documentales. Sus descendientes pueden alternar rfc_runs y plan_runs y contener test_runs con harness_runs bajo cualquier rfc_run según la sección 2; todos conservan el mismo task_run y workflow_run ancestrales.

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

Una TASK se identifica como `TASK-nnnnn`, con cinco cifras y ceros iniciales que numera el contador `task` de la sección 3, y se almacena en el directorio `tasks/` del proyecto en formato Markdown con frontmatter YAML:

```
tasks/TASK-00001.md
```

### Estructura y reglas

La estructura completa de una TASK, sus campos y las reglas de cumplimentación se definen en [TASK_TEMPLATE.md](templates/TASK_TEMPLATE.md). Referirse a la plantilla como fuente de verdad.

### Creación con la CLI

`hactors create-task` escribe ese archivo con su cabecera: consume el contador `task` de la sección 3 y acepta `--task` y `--actor`. Exige un proyecto activo y su directorio `tasks/`; no cambia el estado activo ni depende de una instancia activa, porque una TASK no es una instancia de ejecución.

El archivo creado es Markdown con la cabecera en frontmatter YAML, seguida de una remisión a la plantilla de estructura. Los valores iniciales proceden de [task_template.yaml](templates/task_template.yaml); el comando no copia la cumplimentación de [TASK_TEMPLATE.md](templates/TASK_TEMPLATE.md) ni redacta su contenido.

Las opciones `--task` y `--actor` se registran literalmente, sin validar el ejecutor contra las etiquetas de [DEFINITIONS.md](DEFINITIONS.md) ni la descripción contra ningún formato. Si se omiten, conservan los valores de la plantilla; un valor vacío explícito sustituye el valor de ese campo. `rfcs`, `required_knowledge`, `deliverables`, `acceptance_criteria` y `execution` proceden siempre de la plantilla: el comando no declara el alcance, no deriva el conocimiento requerido de las RFC, no lista entregables ni criterios y no registra el estado observado ni su objetivo.

Crear el archivo no satisface por sí solo lo que [LIFECYCLE.md](LIFECYCLE.md#task) exige de una TASK: la cabecera queda estructuralmente válida con campos por resolver, y quien la crea debe completar su alcance y sus criterios. El comando no la aprueba ni la inicia: `execution.status` sale de la plantilla y solo [actor: human] autoriza su aprobación y su cierre. Tampoco resuelve ni valida la referencia `task_ref` que un workflow_run declare hacia ella, no modifica otras TASK ya creadas y no altera `.state.yaml`. Un contador inválido, una plantilla ausente o rota, un directorio `tasks/` ausente o un archivo `TASK-nnnnn.md` ya existente se rechazan sin escribir nada y sin consumir el contador.

### Relación con workflow_run

La TASK es el punto de partida. Cuando se crea un workflow_run, se referencia la TASK que lo inicia mediante el campo `task_ref` en el bloque `identity` del manifiesto del workflow_run:

```yaml
workflow_run_000001:
  identity:
    id: "workflow_run_000001"
    task_ref: "TASK-00001"
```

`hactors create-workflow --task-ref` acepta el identificador de la TASK o la ruta de su archivo en `tasks/` y registra siempre el identificador; cualquier otra forma se rechaza sin crear el workflow_run ni consumir su contador. Un valor vacío sigue siendo válido y deja la asociación pendiente. Normalizar la forma escrita no comprueba que la TASK exista ni certifica su contenido.

Esto inicia la cadena de trazabilidad descrita en la sección 8. Cada nuevo rfc_run, plan_run, test_run o harness_run conserva la TASK iniciadora a través de todos sus ancestros, no mediante una copia de `task_ref` en cada nivel.

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
- **test_run → harness_run → versión de HARNESS**: el primer vínculo es contención; `identity.harness_ref` declara la versión usada y `identity.content_ref` registra la referencia a su contenido, sin convertir el catálogo en padre de la instancia.

### Derivación documental y contención de ejecuciones

Un PLAN propone RFCs mediante `derived_rfcs`, conforme a [PLAN_TEMPLATE.md](templates/PLAN_TEMPLATE.md). Cada RFC derivada conserva su relación documental `derives` con la RFC de origen, según [RFC.md](RFC.md); el PLAN es el documento que organiza esa derivación, no un sustituto de la RFC de origen.

En la ejecución, el padre inmediato del rfc_run derivado es el **plan_run** que lo contiene; el rfc_run de origen es su abuelo. Ambos permanecen en la ruta, junto con cualquier ascendencia anterior. La contención no sustituye las relaciones documentales, no las registra automáticamente y no permite deducir aprobación o dependencias de ejecución.

### Ejemplo completo

Para el árbol recursivo de la sección 2, una TASK `TASK-00001` puede referenciar la RFC inicial y las derivadas involucradas:

```yaml
# tasks/TASK-00001.md
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
    task_ref: "TASK-00001"
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
- Desde un **harness_run**, `harness_ref` identifica la versión de **HARNESS** y el directorio padre lleva al **test_run solicitante**, no al TEST histórico de origen del HRN.
- Desde un **test_run**, `test_ref` identifica el **TEST** y el directorio padre lleva al **rfc_run** correspondiente; se conserva toda su ascendencia, aunque incluya otros rfc_runs.
- Desde un **rfc_run**, `rfc_ref` identifica su **RFC**. Su padre es un **task_run** si es inicial, o un **plan_run** si es derivado; en este último caso se sigue ascendiendo por todos los plan_runs y rfc_runs anteriores, sin colapsarlos por tipo.
- Desde un **task_run**, se navega al padre **workflow_run** y de su `task_ref` se obtiene la **TASK**.
- Desde una **TASK**, se buscan los workflow_runs que la referencian en `task_ref`.
- Desde una **RFC**, un **PLAN** o un **TEST**, se buscan todas sus instancias por `rfc_ref`, `plan_ref` o `test_ref`, respectivamente, recorriendo recursivamente las ramas a cualquier profundidad. Una referencia documental puede devolver varias rutas de ejecución, no una selección activa implícita.
- Desde una **versión de HARNESS**, se buscan las instancias que declaran esa referencia exacta en `harness_ref`. La consulta no valida la publicación, la compatibilidad ni los resultados de esas instancias.

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

Su padre inmediato es un rfc_run, inicial o derivado, y puede contener cero o varios harness_runs según la sección 2. La RFC de contexto se obtiene del padre, sin duplicar `rfc_ref`; la ruta conserva todos los ancestros y determina la profundidad. Un mismo TEST puede tener varias instancias con IDs distintos, bajo el mismo rfc_run o bajo otros rfc_runs cuando el escenario sea compatible.

`create-test-run` crea el directorio y su manifiesto y selecciona la nueva ruta. No genera ni modifica el artefacto TEST, no lo ejecuta y no produce resultados ni evidencia. Las reglas de evidencia se definen en [EVIDENCE.md](EVIDENCE.md); crear una instancia no acredita una verificación satisfactoria ni cierra su RFC.

## 12. harness_run: ejecución de una versión de HARNESS

La CLI crea y selecciona la estructura de `harness_run`; no automatiza la publicación, resolución, verificación o ejecución de recetas. El HARNESS y sus versiones publicadas siguen [HARNESS.md](HARNESS.md); sus campos y referencias exactas se definen en [HRN_TEMPLATE.md](templates/HRN_TEMPLATE.md).

Un `harness_run` registra una instancia concreta del uso de **una versión publicada** de HARNESS. Puede crearse su estructura antes de completar y verificar esa asociación; crearla no acredita que la versión exista o esté publicada. La receta, su versión y la ejecución tienen identidades distintas. El padre es el `test_run` que solicita ese uso, independientemente del TEST que originó el HRN o del lugar donde se almacena su receta.

### Contención y multiplicidad

El anidamiento sigue la tabla de la sección 2:

- Cada `harness_run` tiene un solo `test_run` padre, bajo una RFC inicial o derivada a cualquier profundidad. No se anida directamente bajo `rfc_run`, `plan_run`, el catálogo HRN o una carpeta de versión.
- Un TEST puede usar distintos HRN o distintas versiones, y repetir un uso; cada uso concreto obtiene otro `harness_run`. Para repetir el TEST completo se crea además otro `test_run`.
- Dos TESTs pueden usar la misma versión, pero cada contexto conserva sus propias instancias. No se mueve, comparte o reutiliza un directorio de ejecución como hijo de otro TEST.
- La instancia conserva la ubicación e identidad de todos sus ancestros. La reutilización de la receta es una referencia documental, no un segundo padre ni una rama que salte al TEST de origen.

El árbol y las profundidades se muestran en la sección 2, y su creación en la secuencia CLI de la sección 4. Los tres harness_runs pueden referenciar `HRN-00001@v002` sin compartir su ejecución. Cada harness_run suma un nivel al TEST solicitante; los ancestros RFC/PLAN repetidos conservan sus posiciones.

### Contrato del manifiesto

Cada instancia conserva su propio `manifest.yaml`, cuya estructura y valores iniciales proceden de [harness_run_template.yaml](templates/harness_run_template.yaml). Los campos son:

| Campo | Responsabilidad |
|---|---|
| `identity.id` | ID `harness_run_` con un mínimo de seis dígitos; coincide con el directorio. |
| `identity.harness_ref` | Referencia exacta a la versión publicada, con la notación de HRN_TEMPLATE; nunca `current`, `latest` ni un HRN sin versión. |
| `identity.content_ref` | Referencia al contenido inmutable resuelta al asociar la versión; coincide con la asociación publicada en el catálogo y queda fijada para esta ejecución. |
| `execution.source_revision` | Revisión exacta examinada, no la revisión de la receta ni un tag o rama mutable. |
| `execution.parameters` | Valores efectivos de los parámetros admitidos por la receta, incluidos los predeterminados utilizados. |
| `state.status` | Estado de esta instancia, independiente del estado de disponibilidad de la versión y del resultado del TEST. |
| `state.blocked_reason` | Motivo de bloqueo de esta instancia, cuando corresponda. |

El TEST solicitante se obtiene de `identity.test_ref` en el padre; la RFC y la TASK se recuperan siguiendo la ruta y sus manifiestos. No se duplican `test_ref`, `rfc_ref`, `task_ref`, origen del HRN, padre, ascendencia ni profundidad en el harness_run.

Antes de ejecutar deben quedar resueltas las referencias documentales del contexto, la versión publicada, su contenido conservado, la revisión examinada y los parámetros efectivos. Publicar un `draft` permite verificar esa versión concreta sin declarar que ya es reproducible. Se comprueba que el contenido coincide con lo fijado; una discrepancia no se corrige apuntando silenciosamente a otra versión. No se ejecuta un borrador mutable bajo una identidad que después cambiará de contenido.

La referencia de contenido se conserva como registro histórico de lo seleccionado, no como un segundo catálogo editable. Una vez iniciado el uso no se cambia su versión, revisión o parametrización para representar otro intento: se crea otra instancia. El estado puede evolucionar sin reescribir lo observado.

### Creación, numeración y contexto activo

`create-harness-run` exige que la instancia seleccionada sea un `test_run`, añade un único componente y selecciona el nuevo hijo; no busca un TEST ancestral compatible. Usa el contador global `harness_run` de la sección 3, también en proyectos anteriores que todavía no lo tengan. Ascender quita solo el harness_run y vuelve al TEST solicitante.

Las opciones `--harness-ref` y `--content-ref` registran literalmente las referencias declaradas. Si se omiten, conservan los valores de la plantilla; un valor vacío explícito sustituye el valor de ese campo. La creación no comprueba su sintaxis, existencia, publicación, correspondencia con el catálogo ni hashes, y no resuelve alias de versión vigente. Los campos de revisión y parámetros efectivos también proceden de la plantilla: no se ejecuta la receta para deducirlos. Las referencias incompletas o inválidas no impiden crear la estructura, pero no satisfacen el contrato de ejecución anterior.

La ruta activa mantiene exactamente los dos campos de la sección 4. Estado resultante de su secuencia CLI:

```yaml
active_project: "mi_proyecto"
active_run_path: "hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001/rfc_run_000002/plan_run_000002/rfc_run_000003/test_run_000002/harness_run_000003"
```

Cambiar de rama o la versión vigente del catálogo no modifica ejecuciones anteriores. El comando no mueve recetas, modifica catálogos, copia ancestros ni registra relaciones documentales automáticamente.

### Resultados y trazabilidad

Crear o seleccionar un harness_run no construye ni ejecuta el HARNESS, no publica versiones, no produce EVD/FND ni aprueba o cierra el TEST o la RFC. La resolución y verificación de recetas, así como la automatización de su ejecución, no están implementadas por este comando.

Las EVD producidas se registran directamente junto a esta instancia. `source.harness` identifica la misma versión que `identity.harness_ref`, y `source.execution` conserva la ruta completa hasta el harness_run, no solo hasta el TEST o la RFC. El contexto observado conserva revisión examinada, construcción, configuración, plataforma, comandos y resultados conforme a [EVIDENCE.md](EVIDENCE.md), sin copiar la receta ni depender de la instalación efímera.

La aplicabilidad a otros criterios o artefactos sigue [EVD_TEMPLATE.md](templates/EVD_TEMPLATE.md); compartir receta no propaga validez. Los FND producidos se registran directamente junto a esta instancia, con esta ejecución como origen y afectados explícitos conforme a [FINDING.md](FINDING.md); no se atribuye un defecto al HRN por el solo hecho de haberlo utilizado.

## 13. Registro de evidencia desde cualquier origen

Una evidencia no es una instancia de ejecución: no se anida, no tiene hijos ni cambia el contexto activo. Pertenece al proyecto y se escribe junto al artefacto o la ejecución que la originó, conforme a [EVIDENCE.md](EVIDENCE.md); su esquema y tipos se definen únicamente en [EVD_TEMPLATE.md](templates/EVD_TEMPLATE.md).

`create-evidence` exige un proyecto activo y un origen: una ruta relativa al proyecto, sin `.` ni `..`, separadores alternativos ni componentes vacíos. `--origin` declara esa ruta; si se omite, el origen es la ruta de la instancia activa, que entonces debe existir. En ambos casos el origen determina a la vez la ubicación del registro y el campo de procedencia:

| `--origin` | Validación | Campo de procedencia | Ubicación del archivo |
|------------|------------|----------------------|-----------------------|
| Ruta con el prefijo `hactors/` | Ruta de ejecución completa válida, con la validación de la sección 4 | `source.execution` | El directorio de esa instancia |
| Cualquier otra ruta del proyecto | Debe existir y no ser un enlace simbólico | `source.artifact`, literal | Su propio directorio, o el padre si es un archivo |

Un origen que empieza por `hactors/` se trata siempre como ejecución: si la ruta es inválida se rechaza, sin reinterpretarla como artefacto. `hactors` a secas no identifica ni una ejecución ni un artefacto. Omitir `--origin` toma la ruta activa completa tal como está, sin ascender a un ancestro ni descender a un hijo; un `--origin` vacío explícito sigue siendo un origen inválido y no se confunde con la omisión. Tomar la instancia activa como origen no modifica la selección. El comando no registra rutas absolutas, referencias externas ni revisiones de Git como ubicación.

Cada evidencia se escribe en su propio archivo `EVD-nnnnn.yaml`, con el ID del contador global `evidence` de la sección 3; la numeración es única en el proyecto aunque los archivos queden repartidos en varios directorios. El comando no crea un directorio central de evidencias ni subdirectorios por tipo.

Las opciones `--title`, `--kind` y `--recorded` se registran literalmente, sin validar el tipo contra la tabla normativa ni el formato de la fecha. Si se omiten, conservan los valores de [evidence_template.yaml](templates/evidence_template.yaml); un valor vacío explícito sustituye el valor de ese campo. `relations`, `environment` y el resto de `source` proceden siempre de la plantilla: el comando no declara aplicabilidad, no captura plataforma, comandos ni salidas, y no rellena `source.rfc`, `source.harness` ni `source.commit` a partir de la ascendencia o del manifiesto del origen.

Crear el archivo no satisface por sí solo los mínimos de [EVIDENCE.md](EVIDENCE.md): el registro queda estructuralmente válido con campos por resolver, y quien registra debe completar el contexto observado y las relaciones de aplicabilidad. El comando no ejecuta pruebas ni recetas, no modifica el artefacto de origen, no altera `.state.yaml`, no consume contadores de ejecución ni registra relaciones en el manifest del proyecto. Un origen inválido, la ausencia de instancia activa cuando `--origin` se omite, una plantilla ausente o rota, un contador inválido o un archivo `EVD-nnnnn.yaml` ya existente en el directorio de destino se rechazan sin escribir nada y sin consumir el contador.

## 14. Registro de hallazgos desde cualquier origen

Un hallazgo no es una instancia de ejecución: no se anida, no tiene hijos ni cambia el contexto activo. Pertenece al proyecto y se escribe junto al artefacto o la ejecución que lo originó, conforme a [FINDING.md](FINDING.md); su esquema, campos, tipos, severidades y estados se definen únicamente en [FND_TEMPLATE.md](templates/FND_TEMPLATE.md).

`create-finding` exige un proyecto activo y un origen: una ruta relativa al proyecto, sin `.` ni `..`, separadores alternativos ni componentes vacíos. `--origin` declara esa ruta; si se omite, el origen es la ruta de la instancia activa, que entonces debe existir. Las reglas de validación son las de la sección 13, y el origen determina a la vez la ubicación del registro y el campo de procedencia:

| `--origin` | Validación | Campo de procedencia | Ubicación del archivo |
|------------|------------|----------------------|-----------------------|
| Ruta con el prefijo `hactors/` | Ruta de ejecución completa válida, con la validación de la sección 4 | `source.execution` | El directorio de esa instancia |
| Cualquier otra ruta del proyecto | Debe existir y no ser un enlace simbólico | `source.artifact`, literal | Su propio directorio, o el padre si es un archivo |

Un origen que empieza por `hactors/` se trata siempre como ejecución: si la ruta es inválida se rechaza, sin reinterpretarla como artefacto. `hactors` a secas no identifica ni una ejecución ni un artefacto. Omitir `--origin` toma la ruta activa completa tal como está, sin ascender a un ancestro ni descender a un hijo; un `--origin` vacío explícito sigue siendo un origen inválido y no se confunde con la omisión. Tomar la instancia activa como origen no modifica la selección. El comando no registra rutas absolutas ni referencias externas como procedencia.

Cada hallazgo se escribe en su propio archivo `FND-nnnnn.yaml`, con el ID del contador global `finding` de la sección 3; la numeración es única en el proyecto aunque los archivos queden repartidos en varios directorios. El comando no crea un registro central de hallazgos ni subdirectorios por tipo.

Las opciones `--title`, `--kind`, `--severity`, `--opened` y `--updated` se registran literalmente, sin validar el tipo ni la severidad contra sus tablas normativas ni el formato de las fechas. Si se omiten, conservan los valores de [finding_template.yaml](templates/finding_template.yaml); un valor vacío explícito sustituye el valor de ese campo. `state`, `actions`, `relations`, `resolved` y el resto de `source` proceden siempre de la plantilla: el comando no declara afectados, no asocia acciones, no cierra el hallazgo y no rellena `source.workflow`, `source.task` ni `source.rfc` a partir de la ascendencia o del manifiesto del origen.

Crear el archivo no satisface por sí solo los mínimos de [FINDING.md](FINDING.md): el registro queda estructuralmente válido con campos por resolver, y quien registra debe completar la afectación y el contexto documental. El comando no resuelve ni valida las referencias declaradas, no modifica el artefacto de origen ni otros hallazgos ya registrados, no altera `.state.yaml`, no consume contadores de ejecución ni registra relaciones en el manifest del proyecto. Un origen inválido, la ausencia de instancia activa cuando `--origin` se omite, una plantilla ausente o rota, un contador inválido o un archivo `FND-nnnnn.yaml` ya existente en el directorio de destino se rechazan sin escribir nada y sin consumir el contador.

## 15. Creación del archivo de resumen

Un resumen no es una instancia de ejecución: no se anida, no tiene hijos ni cambia el contexto activo. Pertenece al proyecto y se escribe junto al artefacto que resume, conforme a [SUMMARY.md](SUMMARY.md); su estructura y sus secciones se definen únicamente en [SUMMARY_TEMPLATE.md](templates/SUMMARY_TEMPLATE.md).

`create-summary` exige un proyecto activo y un origen: una ruta relativa al proyecto, sin `.` ni `..`, separadores alternativos ni componentes vacíos. `--origin` declara esa ruta; si se omite, el origen es el workflow_run de la instancia activa, tomado como sus dos primeros componentes. Como solo existen dos niveles, el origen admitido es más estrecho que el de las secciones 13 y 14:

| `--origin` | Validación | `level` | Archivo creado |
|------------|------------|---------|----------------|
| `hactors/workflow_run_XXXXXX` | Ruta de ejecución completa válida, con la validación de la sección 4 | `workflow_run` | `SUMMARY.md` en el directorio de esa instancia |
| `rfcs/<archivo>.md` | Debe existir, ser un archivo y no ser un enlace simbólico | `rfc` | `rfcs/<nombre-sin-extension> - Summary.md`, junto a la RFC |

Cualquier otra instancia de ejecución se rechaza: lo registrado en un `task_run`, `rfc_run`, `plan_run`, `test_run` o `harness_run` se agrega al resumen de su RFC o al global, conforme a [SUMMARY.md](SUMMARY.md#niveles). Un artefacto fuera de `rfcs/` también se rechaza, porque el nivel 1 existe únicamente por RFC. Un origen que empieza por `hactors/` se trata siempre como ejecución: si la ruta es inválida se rechaza, sin reinterpretarla como artefacto. Un `--origin` vacío explícito sigue siendo un origen inválido y no se confunde con la omisión. Tomar la instancia activa como origen no modifica la selección. El comando no registra rutas absolutas ni referencias externas como identidad del artefacto resumido.

El archivo creado es Markdown con la cabecera en frontmatter YAML, seguida de una remisión a la plantilla de estructura. Los valores iniciales de la cabecera proceden de [summary_template.yaml](templates/summary_template.yaml); el comando no copia las secciones de [SUMMARY_TEMPLATE.md](templates/SUMMARY_TEMPLATE.md) ni redacta su contenido. `artifact` reproduce literalmente el origen y `level` se deriva de él; ninguno de los dos es una opción declarable. Un resumen no tiene identidad ni contador propios, así que el comando no consume ninguno y el archivo se nombra por el artefacto que resume.

Las opciones `--title`, `--status`, `--final-state`, `--target-state` y `--date` se registran literalmente, sin validar la fase ni el estado final contra [LIFECYCLE.md](LIFECYCLE.md), el estado final contra `global_state.status` del manifiesto, ni el formato de la fecha. Si se omiten, conservan los valores de la plantilla; un valor vacío explícito sustituye el valor de ese campo.

Crear el archivo no satisface por sí solo los mínimos de [SUMMARY.md](SUMMARY.md): la síntesis, las referencias y la matriz de trazabilidad las redacta quien resume. El comando no declara la consolidación, que corresponde a [actor: human], no reproduce el manifiesto del workflow_run, no agrega el historial de ejecuciones, no modifica el artefacto resumido ni otros resúmenes ya creados, no altera `.state.yaml` y no ejecuta Git ni asume que existe un repositorio Git. Un origen inválido, la ausencia de instancia activa cuando `--origin` se omite, una plantilla ausente o rota, o un archivo de resumen ya existente en el destino se rechazan sin escribir nada.
