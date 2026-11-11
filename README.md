# HACTORS - Human–AI Collaboration Through RFC Specifications

Construye trazabilidad de proyectos. No historiales de prompts.

---

## ¿Qué es HACTORS?

HACTORS es un enfoque metodológico basado en especificaciones para desarrollar proyectos complejos mediante una colaboración estructurada entre humanos e IA.

HACTORS es un sistema de gobernanza y trazabilidad de los proyectos que lo adoptan. Define qué reglas hay que seguir, cómo se propone un requerimiento (RFC), cómo se organiza (WORKFLOW y TASK), cómo se ejecutan las acciones derivadas y cómo los cambios triviales bypassan el flujo completo (TRV).

HACTORS no reduce necesariamente la cantidad de información que necesita un actor human/agent para realizar una tarea. Reduce la cantidad de información que el actor humano tiene que proporcionar explícitamente en cada tarea.

HACTORS no solamente describe qué debe hacerse y cómo debe hacerse; también permite determinar dónde consta cada decisión y bajo qué contexto.

La autoría registrada identifica quién redactó un artefacto, no quién realizó cada operación: ningún campo acredita al operador de un cambio de estado y la CLI no autentica a quien la invoca. Una etiqueta de actor indica elegibilidad, no autorización, conforme a [HACTORS_SYSTEM.md](specs/HACTORS_SYSTEM.md#17-transición-de-estados-documentales).

---

## Propósito

Su propósito está fundamentado en la necesidad de que toda modificación al proyecto —código, documentación, arquitectura— tenga una decisión contratada, evidencia verificable y trazabilidad entre niveles. El proceso es común a toda instancia: lo concreto de cada una vive en su capa de proyecto y en los paquetes de perfil que componga.

---

## Cómo está organizado HACTORS.

```
hactors/
├── docs/        Guías, tutoriales y referencia rápida.
├── projects/    Proyectos gestionados, estado activo, artefactos, evidencias, hallazgos, decisiones, historial.
├── specs/       Normativa y plantillas.
├── tools/       La CLI y el visor servido.
└── README.md    Este documento.
```

### `docs/` — Cómo usar HACTORS.

Guías aún no incorporadas al repositorio; su migración está registrada en [TODO.md](TODO.md).

| Archivo | Contenido |
|---|---|
| QUICKSTARTER.md | Tutorial paso a paso: primera RFC, primer TRV. |
| CHEAT_SHEET.md | Tabla de decisión: qué artefacto usar según la situación. |
| LIFECYCLE_DIAGRAMS.md | Diagramas Mermaid del flujo completo y ciclos de vida. |
| EXAMPLES.md | Ejemplo real extremo a extremo con RFC-A00001. |
| TOOLS.md | Herramientas disponibles y plan de CI. |

### `projects/` — Proyectos basados en HACTORS.

Cada subdirectorio es un proyecto HACTORS con su propia identidad, artefactos, RFCs, estándares específicos, manifiesto de relaciones y flujo de ejecución; la excepción es `views/`, que reúne las vistas derivadas de la raíz y no es un proyecto. Ver [PROJECTS.md](specs/PROJECTS.md) y [VIEWS.md](specs/VIEWS.md).

### `specs/` — Contenido normativo.

Especificaciones y plantillas que rigen la metodología HACTORS y la estructura de los proyectos: veintisiete especificaciones normativas en `specs/` —la política de lectura que las ordena, en [CONTEXT_LOADING.md](specs/CONTEXT_LOADING.md)— y las plantillas documentales y YAML de los artefactos y de las instancias de ejecución en `specs/templates/`. Los perfiles técnicos no viven aquí: los compone cada proyecto en su `standards/`, conforme a [STANDARDS.md](specs/STANDARDS.md).

### `tools/` — La CLI y el visor servido.

Herramientas de automatización para la gestión de proyectos HACTORS. La [CLI](tools/cli/) permite crear y seleccionar proyectos (`create-project`, `use-project`), crear la TASK iniciadora (`create-task`), crear instancias de ejecución (`create-workflow`, `create-task-run`, `create-rfc-run`, `create-plan-run`, `create-test-run`, `create-harness-run`), seleccionar su ruta activa completa o ascender al padre (`use-run`), registrar evidencias junto a su origen (`create-evidence`), registrar hallazgos junto a su origen (`create-finding`), crear el archivo de resumen de una RFC o de un workflow_run (`create-summary`), añadir una acción derivada al campo `actions:` de una RFC (`create-action`), crear una decisión en `decisions/` (`create-adr`), registrar una arista del grafo del proyecto (`relate`), reescribir el estado documental de un artefacto o de una acción derivada (`transition`), comprobar el proyecto activo (`validate`), proyectar su modelo de lectura (`export`) y dibujar el visor de la raíz con el tablero de cada proyecto (`render`). El [visor servido](tools/viewer/) dibuja por HTTP la misma proyección que `export` calcula: bajo la cabecera —que lleva el selector del proyecto activo—, un panel de wildcards a todo el ancho con las cifras del ámbito consultado, y debajo tres columnas —los proyectos de la raíz a la izquierda, la vista al centro y a la derecha las operaciones que ejecuta (fijar el proyecto activo, su única escritura) junto a los comandos de la CLI que solo muestra—, conforme a [VIEWS.md](specs/VIEWS.md#el-visor-servido). La jerarquía recursiva RFC/PLAN con TEST bajo RFC y HARNESS bajo TEST, el contexto activo y la secuencia de uso se describen en [HACTORS_SYSTEM.md](specs/HACTORS_SYSTEM.md); las vistas derivadas, en [VIEWS.md](specs/VIEWS.md). Crear una TASK no declara su alcance ni sus criterios y no la aprueba; crear instancias HARNESS no publica ni ejecuta recetas ni verifica su contenido; registrar una evidencia no captura su contexto observado ni declara su aplicabilidad; registrar un hallazgo no declara sus afectados ni cambia su estado; crear un resumen no redacta sus secciones ni declara su consolidación; crear una acción no produce su entregable ni la completa; crear una decisión no redacta sus secciones ni la aprueba; registrar una arista no resuelve su origen ni valida su tipo; transicionar un artefacto no decide su transición ni la propaga, no acredita a quien la realiza y no escribe su historial; validar no repara las inconsistencias que denuncia; exportar no dibuja ninguna vista ni repara lo que proyecta; renderizar no escribe el modelo de lectura ni omite un proyecto que no se pueda proyectar.



```
HACTORS
│
├── Human–AI collaboration
│
├── RFC Specifications
│
└── Project evolution
    ↑
    └── result of the process
```

```
RFC → artifacts → evidence → decisions → evolution → new project status
```

```
SPECS = specifications system/metamodel
HACTORS = Human-AI collaboration project/methodology
RFCs = structural unit of evolution
Artifacts / Evidence / Decisions = traceability mechanisms
```

Los [artefactos](specs/ARTIFACTS.md) contienen conocimiento; cada artefacto y cada instancia portan su propia identidad y estado; las relaciones contienen estructura.

La provenance debe ser preservable y auditable, pero no necesariamente embebida en el artefacto que la describe.