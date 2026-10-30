# Definiciones.

## Propósito

Define el vocabulario compartido. Los documentos enlazados establecen las reglas operativas de cada concepto.
Los identificadores técnicos se conservan aunque la explicación esté en castellano.
Esta lista no añade requisitos: cuando una entrada discrepe de la especificación del artefacto, prevalece aquella.

## Actores

Un **actor** es el sujeto que puede ejecutar una acción dentro del proceso.
La etiqueta indica elegibilidad, no obliga a ejecutar la acción ni sustituye el alcance o la autorización de una tarea.

| Etiqueta | Significado |
|---|---|
| `[actor: human]` | Persona responsable, con la autoridad necesaria para la acción. |
| `[actor: agent]` | Agente de IA que ejecuta trabajo dentro de los límites autorizados. |
| `[actor: ci]` | Automatización que ejecuta comprobaciones u operaciones definidas, sin juicio de aprobación. |
| `[actor: ...]` | Prohibición total para todos los actores; no es un marcador por completar. |

Las combinaciones usan `|`: `[actor: human | agent]` permite cualquiera de ambos ejecutores.
`[actor: human | agent | ci]` incluye los tres, sin exigir su participación simultánea.
La etiqueta puede preceder o seguir a una acción; en tablas Markdown se escapa el separador como `\|`.
Una etiqueta puede gobernar una sección si su alcance se declara expresamente.
Sin etiqueta, una definición o restricción técnica no concede permisos de ejecución.

La **autoría** identifica quién redactó; la **aprobación** habilita una decisión; la **ejecución** realiza el trabajo.
Son responsabilidades distintas, incluso cuando recaen sobre una misma persona.
Las asignaciones concretas se establecen en WORKFLOW.md y en [LIFECYCLE.md](LIFECYCLE.md).

## Nomenclatura

Un **artefacto** se identifica en mayúsculas con cinco cifras y ceros iniciales: `TASK-nnnnn`, `RFC-Xnnnnn`, `AC-nnnnn`, `PLAN-nnnnn`, `ADR-nnnnn`, `EVD-nnnnn`, `FND-nnnnn` y `HRN-nnnnn`, cuya versión publicada se escribe `HRN-nnnnn@vNNN`.
Una **instancia de ejecución** se identifica en minúsculas con seis cifras: `workflow_run_000001`, `task_run_000001`, `rfc_run_000001`, `plan_run_000001`, `test_run_000001` y `harness_run_000001`.
El SUMMARY carece de identidad propia: se identifica por el artefacto que resume.

Un identificador es único en el proyecto y no se reutiliza al retirar el artefacto. El número no codifica parentesco, profundidad ni orden temporal, y la numeración la llevan los contadores del manifest conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#contadores).

En la prosa, un identificador genérico se escribe con cifras `nnnnn`; en una tabla de contadores se escribe un ejemplo real.

## Trabajo y conocimiento

| Término | Definición |
|---|---|
| SPECS | Sistema de especificaciones que organiza reglas, trabajo y conocimiento; es la autoridad normativa que HACTORS aplica. |
| HACTORS | Metodología de colaboración entre personas y sistemas de IA basada en especificaciones RFC; gobernanza y trazabilidad del proyecto que la compone. |
| Proyecto HACTORS | Unidad de trabajo identificable, delimitada y evolutiva cuyo estado se reconstruye a partir de sus artefactos persistentes. Reglas en [PROJECTS.md](PROJECTS.md). |
| Especificación | Documento que establece requisitos, restricciones o procedimientos dentro de un alcance declarado. |
| Norma de proyecto | Convención particular de documentación, Git o estilo que vive en `standards/`; solo redefine reglas con necesidad real y sin contradecir la autoridad normativa de SPECS. |
| Contrato | Interfaz y semántica pública con precondiciones, resultados, errores e invariantes. |
| Artefacto | Resultado identificable del trabajo: documento, código, configuración, registro o evidencia. Los tipos admitidos están en [ARTIFACTS.md](ARTIFACTS.md). |
| WORKFLOW | Proceso abstracto que ordena fases y pasos y agrupa las TASK de un alcance; su cierre es disposición `[actor: human]`. |
| RFC | Propuesta formal de análisis, cambio o trabajo, con alcance, decisiones y aceptación verificable. Convenciones en [RFC.md](RFC.md). |
| TASK (`TASK-nnnnn`) | Artefacto iniciador: toda ejecución nace de una TASK, que delimita una unidad de trabajo y sus criterios de aceptación. Reglas en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#7-task-artefacto-iniciador). |
| Acción derivada (`AC-nnnnn`) | Entregable individual bajo una RFC: análisis, plan, decisión, implementación, prueba, evidencia o documentación. |
| Plan (`PLAN-nnnnn`) | Secuencia ordenada de pasos con puntos de decisión; artefacto revisable derivado de una RFC. Formato en [templates/PLAN_TEMPLATE.md](templates/PLAN_TEMPLATE.md). |
| DECISION (`ADR-nnnnn`) | Registro de una decisión, sus alternativas y sus consecuencias, en su propio archivo dentro de `decisions/`. Reglas en [DECISIONS.md](DECISIONS.md). |
| TEST | Verificación identificable e inmutable en su contenido y propósito; adaptarla a otro objetivo produce un TEST nuevo que referencia al anterior. Reglas en [TESTS.md](TESTS.md). |
| HARNESS (`HRN-nnnnn`) | Receta persistente con versiones publicadas inmutables, independiente del harness construido, que es efímero. Reglas en [HARNESS.md](HARNESS.md). |
| Evidencia (`EVD-nnnnn`) | Registro comprobable de una observación o ejecución, con su procedencia y su aplicabilidad. Reglas en [EVIDENCE.md](EVIDENCE.md). |
| Hallazgo (`FND-nnnnn`) | Hecho observado que requiere tratamiento, con tipo, severidad y estado; no interpreta, no aprueba cambios ni sustituye una RFC. Reglas en [FINDING.md](FINDING.md). |
| SUMMARY | Síntesis del resultado de un artefacto: qué se pretendía, qué se alcanzó, qué lo respalda y qué queda pendiente. Reglas en [SUMMARY.md](SUMMARY.md). |
| Instancia de ejecución | Ejecución concreta e identificable de un artefacto, con estado observable y resultados registrables; ejecutar de nuevo un documento exige otra instancia. |
| `workflow_run` | Instancia concreta de un WORKFLOW; registra el estado global, los pasos y los intentos de la ejecución. |
| `task_run` | Unidad de trabajo dentro de un workflow_run que contiene ejecuciones de RFC. |
| `rfc_run` | Instancia de ejecución de una RFC, dentro de un task_run o de un plan_run. |
| `plan_run` | Instancia de ejecución de un PLAN, dentro de un rfc_run; puede contener ejecuciones de RFC derivadas. |
| `test_run` | Instancia de ejecución de un TEST, dentro de un rfc_run inicial o derivado; puede contener harness_runs. |
| `harness_run` | Instancia de uso de una versión de HARNESS bajo el test_run solicitante; hoja de la ejecución. |
| Manifiesto | Archivo `manifest.yaml` que registra identidad, relaciones y contadores; existe uno en la raíz del proyecto y uno por cada instancia de ejecución. |
| Estado activo | Contexto de trabajo actual en `projects/.state.yaml`: el proyecto seleccionado y la ruta completa de la instancia activa con sus ancestros. |
| Relación | Vínculo identificable entre dos artefactos, con su tipo y su ubicación física, registrado en el grafo del proyecto. |
| Criterio de aceptación | Condición verificable necesaria para aceptar el resultado de un trabajo. |
| Validación | Contraste explícito de los resultados con los criterios de aceptación aplicables. |
| Dependencia normativa | Fuente cuyo contenido es necesario para interpretar o ejecutar correctamente una obligación. |
| Referencia informativa | Fuente de contexto o historia que no añade por sí misma requisitos. |
| Ensamblaje de contexto | Selección y lectura de las dependencias necesarias para una tarea. |
| Cambio trivial (`TRV-nnnnn`) | Corrección de bajo impacto por vía rápida; no produce RFC, TASK ni WORKFLOW. Norma en TRIVIAL.md. |

Los estados de RFC, TASK, SUMMARY y WORKFLOW se definen en [LIFECYCLE.md](LIFECYCLE.md).
Los estados de una acción derivada y la jerarquía con sus invariantes, en PROJECT_STATE.md.
Los tipos de relación admitidos, en RELATIONSHIPS.md.
Los tipos, severidades y estados de un hallazgo, en [templates/FND_TEMPLATE.md](templates/FND_TEMPLATE.md).
La autoridad y conservación de los artefactos, en [ARTIFACTS.md](ARTIFACTS.md).
La jerarquía de ejecución y sus reglas de anidamiento, en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#reglas-de-anidamiento).

La distinción entre el WORKFLOW abstracto y su instancia `workflow_run` se define en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relación-entre-workflow-y-workflow_run).

## Vocabulario normativo

- **Debe / no debe:** obligación o prohibición dentro del alcance indicado.
- **Se recomienda / preferir:** criterio predeterminado cuya desviación debe justificarse.
- **Puede:** alternativa permitida, no obligatoria.
- **Ejemplo:** ilustración que no sustituye una regla ni demuestra una implementación existente.
- **Pendiente:** contenido aún no definido; no equivale a cumplimiento ni a autorización para inferirlo.

## Vocabulario del proyecto COSA

Términos del proyecto COSA, el escenario inicial de construcción de HACTORS. Pertenecen a esa instancia y no forman parte del vocabulario común: un proyecto HACTORS no necesita ser un proyecto de software, conforme a [PROJECTS.md](PROJECTS.md).

| Término | Definición en COSA |
|---|---|
| COSA | Sistema Operativo Cognitivo con IA. |
| Microkernel | Núcleo mínimo que coordina servicios mediante contratos y mantiene separadas sus responsabilidades. |
| SAL | Capa de abstracción sobre primitivas del sistema operativo o plataforma. |
| Syscall | Contrato de servicio para solicitar una operación sobre recursos del sistema. |
| IPC | Comunicación entre procesos mediante mecanismos y formatos definidos. |
| Drenaje | Fase de ejecución entre dejar de aceptar trabajo nuevo y la parada, donde las operaciones pendientes se completan o cancelan; no es un estado de RFC, TASK ni WORKFLOW. |
| Planificación | Reparto del progreso entre componentes concurrentes; el mecanismo concreto pertenece a los contratos del módulo y no se confunde con el Plan (`PLAN-nnnnn`) de una acción derivada. |
| Capacidad | Credencial verificable que representa autoridad sobre operaciones o recursos determinados. |
| Motor de políticas | Componente que evalúa las condiciones de autorización de una operación. |
| Formato de transmisión | Disposición binaria contractual de datos intercambiados o compartidos. |
| POD | Término tradicional de C++; no garantiza por sí solo tamaño, alineación ni portabilidad binaria. |
| Fachada | Vista de dominio que permite consultar datos sin asumir su propiedad. |
| Builder | Constructor que ensambla objetos y comprueba sus invariantes. |
| Descriptor | Lector no propietario que interpreta un búfer conforme a un contrato. |
| Copia cero | Propiedad definida para una ruta concreta que evita copias de la carga útil; no prohíbe toda copia escalar. |
| Identificador fuerte | Tipo que distingue identidades de dominios diferentes y evita intercambios accidentales. |
| Referencia de memoria compartida | Descriptor que identifica una región compartida, su desplazamiento y extensión. |
| Entorno de ejecución de IA | Infraestructura que coordina inferencia, solicitudes y acciones de agentes. |
| Habilidad | Unidad declarada de instrucciones y capacidades invocable por un agente. |

Los tamaños binarios, algoritmos y garantías concretas pertenecen a los contratos vigentes del módulo, no a estas definiciones.
