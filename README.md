# HACTORS - Human–AI Collaboration Through RFC Specifications

Construye trazabilidad de proyectos. No historiales de prompts.

---

## ¿Qué es HACTORS?

HACTORS es un enfoque metodológico basado en especificaciones para desarrollar proyectos complejos mediante una colaboración estructurada entre humanos e IA.

HACTORS es un sistema de gobernanza y trazabilidad de la instancia que lo compone. Define qué reglas hay que seguir, cómo se propone un requerimiento (RFC), cómo se organiza (WORKFLOW y TASK), cómo se ejecutan las acciones derivadas y cómo los cambios triviales bypassan el flujo completo (TRV).

HACTORS no reduce necesariamente la cantidad de información que necesita un actor human/agent para realizar una tarea. Reduce la cantidad de información que el actor humano tiene que proporcionar explícitamente en cada tarea.

HACTORS no solamente describe qué debe hacerse y cómo debe hacerse; también permite determinar quién produjo cada decisión y bajo qué contexto.

La identidad registrada describe quién realizó una operación; no debe ser una declaración libre del propio actor human/agent.

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
├── tools/       Scripts de validación y CI.
└── README.md    Este documento.
```

### `docs/` — Cómo usar HACTORS.

| Archivo | Contenido |
|---|---|
| [QUICKSTARTER.md](docs/QUICKSTARTER.md) | Tutorial paso a paso: primera RFC, primer TRV. |
| [CHEAT_SHEET.md](docs/CHEAT_SHEET.md) | Tabla de decisión: qué artefacto usar según la situación. |
| [LIFECYCLE_DIAGRAMS.md](docs/LIFECYCLE_DIAGRAMS.md) | Diagramas Mermaid del flujo completo y ciclos de vida. |
| [EXAMPLES.md](docs/EXAMPLES.md) | Ejemplo real extremo a extremo con RFC-A00001. |
| [TOOLS.md](docs/TOOLS.md) | Herramientas disponibles y plan de CI. |

### `projects/` — Instancias de proyectos basados en HACTORS.

Cada subdirectorio es un proyecto HACTORS con su propia identidad, artefactos, RFCs, estándares específicos, manifiesto de relaciones y flujo de ejecución. Ver [PROJECTS.md](specs/PROJECTS.md).

### `specs/` — Contenido normativo.

Especificaciones, plantillas y estándares que rigen la metodología HACTORS y la estructura de los proyectos. Actualmente contiene [PROJECTS.md](specs/PROJECTS.md) como única especificación normativa; las demás se incorporarán progresivamente.

### `tools/` — Herramientas disponibles y plan de CI.

Herramientas de automatización para la gestión de proyectos HACTORS. La [CLI](tools/cli/) permite crear y seleccionar proyectos (`create-project`, `use-project`), crear instancias de ejecución (`create-workflow`, `create-task-run`, `create-rfc-run`, `create-plan-run`) y seleccionar su ruta activa completa o ascender al padre (`use-run`). La jerarquía recursiva RFC/PLAN, el contexto activo y la secuencia de uso se describen en [HACTORS_SYSTEM.md](specs/HACTORS_SYSTEM.md).



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

Los artefactos(enlace a ARTIFACTS.md) contienen conocimiento; el índice contiene identidad y estado; las relaciones contienen estructura.

La provenance debe ser preservable y auditable, pero no necesariamente embebida en el artefacto que la describe.