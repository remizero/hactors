# Carga de contexto

## Alcance

Este documento define la política de lectura para ejecutar trabajo bajo HACTORS: qué normas se leen siempre, cuáles solo cuando una condición las activa, y qué se hace con las que aún no existen en esta copia.

Es el valor de `required_knowledge.index` en una TASK y de `required_specifications.index` en una RFC. Esa ruta es relativa a la raíz de esta copia y debe adaptarse al instalar SPECS en otro proyecto. Los enlaces de este documento se resuelven respecto a `specs/`.

[actor: human | agent] resuelve el contexto antes de actuar; una automatización recibe las reglas y las entradas necesarias para su comprobación.

Esto no es un índice de estado. El estado de un artefacto se lee del propio artefacto y el de sus ejecuciones, del árbol de instancias, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md); la consulta agregada la responden las vistas derivadas de [VIEWS.md](VIEWS.md). Ninguna pregunta sobre el estado de un proyecto se responde aquí.

Una norma citada **sin enlace** está pendiente de migrar y su deuda consta en [TODO.md](../TODO.md). Su ausencia no autoriza a interpretar su contenido por el título ni a tener la obligación por inexistente.

## Núcleo obligatorio

Leer la TASK o la instrucción y las RFC aplicables; después, en este orden:

1. [FOUNDATIONS.md](FOUNDATIONS.md): restricciones generales.
2. [DEFINITIONS.md](DEFINITIONS.md): vocabulario, artefactos y actores.
3. [ARTIFACTS.md](ARTIFACTS.md): autoridad y conservación de las fuentes.
4. [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md): artefactos, jerarquía de ejecución, manifiestos y comandos.
5. [PROJECTS.md](PROJECTS.md): estructura física de un proyecto.
6. [WORKFLOW.md](WORKFLOW.md): proceso común y puntos de intervención.
7. [PROJECT_STATE.md](PROJECT_STATE.md): jerarquía WORKFLOW → TASK → RFC → acción y sus invariantes de cierre.

La creación de una primera RFC es una tarea de propuesta: no exige una RFC previa sobre sí misma, pero sí una TASK que la inicie, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#7-task-artefacto-iniciador). Una tarea que implementa una decisión necesita además resolver la RFC y sus contratos aplicables. Ante un registro vacío o contradictorio, verificar primero el estado real de los artefactos conforme a [ARTIFACTS.md](ARTIFACTS.md).

## Carga condicional

| Documento | Condición de lectura |
|---|---|
| [RFC.md](RFC.md) | Se crea, modifica o interpreta una RFC: identidad, tipo, derivación y relaciones. |
| [LIFECYCLE.md](LIFECYCLE.md) | Se interpreta o modifica el estado de una RFC, una TASK, un resumen o un WORKFLOW. |
| [TESTS.md](TESTS.md) | Se define un TEST, se asigna su identidad o se ejecuta. |
| [HARNESS.md](HARNESS.md) | Se define, publica o usa una receta de verificación. |
| [FINDING.md](FINDING.md) | Se registra, consulta o resuelve un hallazgo. |
| [EVIDENCE.md](EVIDENCE.md) | Se registra o consulta la evidencia que sostiene una transición de estado o la resolución de un hallazgo. |
| [DECISIONS.md](DECISIONS.md) | Se adopta, revisa, sustituye o registra una decisión. |
| [SUMMARY.md](SUMMARY.md) | Se redacta, consolida o consulta el resumen de una RFC o de un workflow_run. |
| [VIEWS.md](VIEWS.md) | Se proyecta el modelo de lectura o se dibujan el tablero y el visor. |
| [RELATIONSHIPS.md](RELATIONSHIPS.md) | Se declaran, modifican o verifican relaciones entre artefactos. |
| [WORKFLOW.md](WORKFLOW.md) | Se ordenan fases y pasos o se determina un punto de intervención. |
| [PROJECT_STATE.md](PROJECT_STATE.md) | Se interpreta el estado de una acción derivada o una invariante de cierre entre niveles. |
| [RFC_SYSTEM.md](RFC_SYSTEM.md) | Se asigna la identidad de una RFC, se numeran sus modificadores o se representan sus relaciones. |
| [TRANSACTIONS.md](TRANSACTIONS.md) | Se crea o modifica un artefacto o una instancia, se reconcilia el estado o se corrige una escritura interrumpida. |
| [EXCEPTIONS.md](EXCEPTIONS.md) | Se solicita, aprueba o consulta una excepción a una regla o requisito. |
| [TRIVIAL.md](TRIVIAL.md) | Se propone, ejecuta o consulta un cambio trivial por vía rápida. |
| [VERSIONING.md](VERSIONING.md) | Se interpreta o modifica la versión de esquema de un artefacto, se migran datos o se comprueba compatibilidad. |
| [AI.md](AI.md) | Participa un agente de IA. |
| [PROMPTING.md](PROMPTING.md) | Se prepara una instrucción de trabajo para un agente. |
| [DOCUMENTATION.md](DOCUMENTATION.md) | Se crea o actualiza documentación del proyecto. |
| [STANDARDS.md](STANDARDS.md) | Se compone un perfil técnico o se evalúa una excepción a una norma. |

También se leen los contratos y la documentación de los módulos afectados, y las dependencias normativas de lo seleccionado. Las referencias informativas o históricas no activan por sí mismas una lectura recursiva de todo el repositorio.

## Plantillas

| Plantilla | Condición de lectura |
|---|---|
| [templates/RFC_TEMPLATE.md](templates/RFC_TEMPLATE.md) | Se redacta una RFC: metadatos, cuerpo común y acciones derivadas. |
| [templates/RFC-A_TEMPLATE.md](templates/RFC-A_TEMPLATE.md) | La RFC es de tipo análisis (A). |
| [templates/RFC-D_TEMPLATE.md](templates/RFC-D_TEMPLATE.md) | La RFC es de tipo documentación (D). |
| [templates/RFC-F_TEMPLATE.md](templates/RFC-F_TEMPLATE.md) | La RFC es de tipo feature (F). |
| [templates/RFC-I_TEMPLATE.md](templates/RFC-I_TEMPLATE.md) | La RFC es de tipo integración (I). |
| [templates/RFC-T_TEMPLATE.md](templates/RFC-T_TEMPLATE.md) | La RFC es de tipo tests (T). |
| [templates/TASK_TEMPLATE.md](templates/TASK_TEMPLATE.md) | Se redacta una TASK. |
| [templates/PLAN_TEMPLATE.md](templates/PLAN_TEMPLATE.md) | Se redacta o revisa un PLAN. |
| [templates/TEST_TEMPLATE.md](templates/TEST_TEMPLATE.md) | Se redacta un TEST: identidad, propiedad bajo verificación y criterios. |
| [templates/AC_TEMPLATE.md](templates/AC_TEMPLATE.md) | Se registra o actualiza una acción derivada en el campo `actions:` de su RFC. |
| [templates/ADR_TEMPLATE.md](templates/ADR_TEMPLATE.md) | Se redacta una decisión. |
| [templates/SUMMARY_TEMPLATE.md](templates/SUMMARY_TEMPLATE.md) | Se redacta el resumen de una RFC o de un workflow_run. |
| [templates/EVD_TEMPLATE.md](templates/EVD_TEMPLATE.md) | Se registra una evidencia. |
| [templates/FND_TEMPLATE.md](templates/FND_TEMPLATE.md) | Se registra o consulta un hallazgo. |
| [templates/HRN_TEMPLATE.md](templates/HRN_TEMPLATE.md) | Se define o publica una receta HARNESS. |
| [templates/WORKFLOW_TEMPLATE.md](templates/WORKFLOW_TEMPLATE.md) | Se registra una definición de flujo o se publica una de sus versiones. |
| [templates/TRIVIAL_TEMPLATE.md](templates/TRIVIAL_TEMPLATE.md) | Se registra un cambio trivial por vía rápida. |

Las plantillas `*.yaml` del mismo directorio las consume la CLI al crear artefactos e instancias; no se leen como norma ni se editan para registrar contenido.

## Documentos de proyecto

Las convenciones particulares de documentación, Git y estilo de código no son normas de HACTORS: viven en `standards/` de cada proyecto conforme a [PROJECTS.md](PROJECTS.md), y solo redefinen reglas cuando hay necesidad real y sin contradecir esta autoridad normativa.

Este índice no las enumera, porque cada proyecto compone las suyas y una norma de HACTORS no puede conocerlas. Las filas del índice original que apuntaban a la arquitectura, el nombrado, el rendimiento, las dependencias de pruebas, Git, la ubicación de los ADR, el formato de código y los perfiles técnicos del proyecto COSA quedan fuera por esta razón, no por olvido: su destino es el `standards/` de ese proyecto.

## Mecanismos que sustituyen a los del índice original

HACTORS no mantiene índices ni tablas duplicadas a mano. El índice de RFC vigentes, su archivo y el registro de RFC terminales están descartados: el estado de una RFC se lee de la propia RFC y el de sus ejecuciones, del árbol de instancias, y la consulta agregada la responden las vistas generadas conforme a [VIEWS.md](VIEWS.md).

Tampoco hay un documento de contexto por instancia de ejecución. El contexto de un workflow_run, un task_run, un rfc_run y sus descendientes es su `manifest.yaml`, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md).

Los hallazgos y las evidencias ya no son registros agregados: viven como `FND-nnnnn.yaml` y `EVD-nnnnn.yaml` junto a su origen, conforme a [FINDING.md](FINDING.md) y [EVIDENCE.md](EVIDENCE.md).

## Reutilización del contexto

- Conservar el contexto leído mientras siga disponible y vigente; no releer por rutina en cada paso.
- Ampliarlo antes de ejecutar acciones que activen una condición nueva.
- Consultar de nuevo la fuente ante cambios, dudas precisas o pérdida de contexto.
- Un resumen sirve para localizar información, no para omitir requisitos de una fuente obligatoria.
- Si una dependencia necesaria no existe o está vacía, bloquear la parte afectada y solicitar su definición.
