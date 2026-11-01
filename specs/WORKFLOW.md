# Flujo de trabajo

## Alcance

Proceso único para proponer, ejecutar, verificar y cerrar trabajo bajo HACTORS.

Los actores se interpretan conforme a [DEFINITIONS.md](DEFINITIONS.md); las etiquetas no ordenan actuar fuera de una TASK autorizada. Los estados y sus condiciones pertenecen a [LIFECYCLE.md](LIFECYCLE.md) y no se redefinen aquí; la jerarquía y las invariantes de cierre, a [PROJECT_STATE.md](PROJECT_STATE.md).

Este WORKFLOW es el proceso abstracto; su instancia concreta es un `workflow_run` que registra lo observado, incluidos los intentos fallidos y los bloqueos, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relación-entre-workflow-y-workflow_run). Ninguna fase la ejecuta la CLI: los comandos crean y seleccionan instancias y registran artefactos, pero no aprueban, no avanzan ni cierran. Tampoco los decide el comando que escribirá esos estados, normado en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#17-transición-de-estados-documentales): comprueba aristas e invariantes sobre los datos persistidos y deja las condiciones de juicio en el actor.

## Identidad y versiones

Este documento fija las fases normativas del proceso, no los pasos de ninguna versión concreta. Cada definición que un proyecto usa se registra como `WORKFLOW-nnnnn` en `workflows/WORKFLOW-nnnnn/`, con un catálogo `manifest.yaml` y paquetes inmutables `versions/vNNN/workflow.yaml`, conforme a [templates/WORKFLOW_TEMPLATE.md](templates/WORKFLOW_TEMPLATE.md) y a la disposición de [PROJECTS.md](PROJECTS.md).

La versión declara los pasos `step_XXX` que realizan estas fases y las que excluye; un `workflow_run` referencia la versión exacta `WORKFLOW-nnnnn@vNNN` en su `identity.workflow_version` y usa esos identificadores en su `global_state`.

El estado del WORKFLOW, incluida su disposición `closed`, se registra en el `status` del catálogo con los estados de [LIFECYCLE.md](LIFECYCLE.md#workflow-y-acciones-derivadas) y lo transiciona [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#17-transición-de-estados-documentales), cuya comprobación no alcanza la regla 1 de [PROJECT_STATE.md](PROJECT_STATE.md#regla-de-consistencia-entre-niveles). Tampoco existe un comando que cree la definición: la redactan [actor: human | agent], igual que una RFC, un PLAN, un TEST o una receta HARNESS.

## 0. Resolver contexto

1. [actor: human | agent] identifica la TASK o la instrucción y sus RFC aplicables.
2. [actor: human | agent] resuelve la carga conforme a [CONTEXT_LOADING.md](CONTEXT_LOADING.md), los contratos y las dependencias normativas.
3. [actor: human | agent] lee el estado del trabajo conforme a [PROJECT_STATE.md](PROJECT_STATE.md#carga-de-estado) y localiza sus ejecuciones en el árbol de instancias.
4. [actor: human | agent] comprueba alcance, entregables, criterios, autoridad y estado inicial.
5. [actor: human | agent] detiene la acción afectada si falta una fuente necesaria o existe una contradicción sin resolver.

La propuesta de una primera RFC no necesita referenciarse a sí misma, pero sí una TASK que la inicie, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#7-task-artefacto-iniciador).
Las tareas de implementación no pueden sustituir una decisión requerida por supuestos del ejecutor.

## 1. Proponer y aprobar

1. [actor: human | agent] prepara cambios arquitectónicos, módulos, interfaces o refactorizaciones significativas mediante [RFC.md](RFC.md).
2. [actor: human | agent] delimita el trabajo con [RFC_TEMPLATE.md](templates/RFC_TEMPLATE.md), su variante de tipo y [TASK_TEMPLATE.md](templates/TASK_TEMPLATE.md).
3. [actor: human] revisa y aprueba los contratos, el alcance y los criterios antes de habilitar su ejecución.
4. [actor: human | agent] asigna la identidad de la RFC y representa sus aristas en el grafo dentro de la misma operación, conforme a [RFC_SYSTEM.md](RFC_SYSTEM.md).

No existe un comando que cree una RFC: el documento lo redactan [actor: human | agent] desde las plantillas. `hactors create-task` escribe la cabecera de la TASK, no declara su alcance ni sus criterios y no la aprueba, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#7-task-artefacto-iniciador).

## 2. Preparar la ejecución

1. [actor: human | agent] comprueba dependencias, estado del espacio de trabajo y cambios ajenos antes de modificar archivos.
2. [actor: human | agent] crea la rama prevista cuando el proyecto use control de versiones; la CLI no ejecuta Git ni asume que existe un repositorio.
3. [actor: human | agent] crea las instancias que registrarán la ejecución —`create-workflow` con su `task_ref`, `create-task-run` y `create-rfc-run`— conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#selección-y-creación).
4. [actor: human | agent] identifica qué comprobaciones son aplicables al tipo de trabajo y dónde quedará su evidencia.

Crear una instancia no ejecuta su trabajo, no produce resultados ni evidencia y no autoriza la ejecución.

## 3. Producir los entregables

1. [actor: human | agent] concreta especificaciones y contratos públicos aprobados antes de implementar su lógica, cuando el trabajo incluya implementación.
2. [actor: human | agent] aplica las normas activadas por [CONTEXT_LOADING.md](CONTEXT_LOADING.md), incluidas las del proyecto conforme a [STANDARDS.md](STANDARDS.md).
3. [actor: human | agent] realiza incrementos pequeños, funcionales y verificables dentro del alcance autorizado.
4. [actor: human | agent] registra cada acción derivada en el campo `actions:` de su RFC, con `hactors create-action` o a mano incrementando el contador `action` en la misma operación.
5. [actor: human | agent] mantiene el progreso de la TASK sin atribuir a la RFC hitos que solo cumple una parte de ella.
6. [actor: human | agent] solicita decisión si aparece un cambio de contrato, arquitectura o alcance no aprobado.

## 4. Verificar

1. [actor: human | agent | ci] ejecuta las comprobaciones aplicables: los TEST conforme a [TESTS.md](TESTS.md) y las recetas de verificación conforme a [HARNESS.md](HARNESS.md).
2. [actor: human | agent | ci] comprueba compilación, pruebas, analizadores y formato cuando el entregable sea código, según las normas del proyecto.
3. [actor: human | agent] registra resultados, entorno y evidencia junto a su origen con `hactors create-evidence`, incluidos los fallos y las comprobaciones no realizadas.
4. [actor: human | agent] registra como hallazgo lo observado que requiera tratamiento, con `hactors create-finding`, conforme a [FINDING.md](FINDING.md).
5. [actor: human | agent] corrige fallos propios dentro del alcance y repite las comprobaciones afectadas.

No avanzar a revisión como resultado listo para integrar con verificaciones obligatorias en rojo o sin ejecutar.
Un fallo ajeno o una herramienta no disponible se comunica como bloqueo en el `blocked_reason` de la instancia afectada, no como éxito ni como permiso para ampliar el alcance.

## 5. Sincronizar documentación

1. [actor: human | agent] actualiza las capas afectadas conforme a [DOCUMENTATION.md](DOCUMENTATION.md).
2. [actor: human | agent] comprueba referencias, contratos, decisiones y ejemplos antes de solicitar revisión.
3. [actor: human | agent] incluye documentación y entregables relacionados en el mismo cambio de integración.
4. [actor: human | agent] redacta o actualiza el resumen del artefacto conforme a [SUMMARY.md](SUMMARY.md); declararlo consolidado es de [actor: human].

## 6. Solicitar revisión

1. [actor: human | agent] presenta los entregables y su evidencia; si el proyecto usa control de versiones, abre la solicitud de integración por el medio de ese proyecto.
2. [actor: human | agent | ci] ejecuta las comprobaciones de integración previstas; [actor: ci] interviene si existe una canalización configurada y aporta resultados, sin sustituir la aprobación.
3. [actor: human] revisa arquitectura, contratos y suficiencia de la evidencia de aceptación.
4. [actor: human | agent] atiende observaciones de implementación y repite las verificaciones afectadas.
5. [actor: human] determina si una observación cambia el diseño y necesita una nueva decisión.

## 7. Validar e integrar

1. [actor: human] aprueba el resultado cuando los criterios y las revisiones exigidas están satisfechos.
2. [actor: human] integra el cambio conforme al control de versiones del proyecto, si la tarea incluye integración.
3. [actor: human | agent] registra la aceptación en el bloque `review` del manifiesto del workflow_run y, cuando aplique, la referencia de integración en su bloque `integration`.

En trabajo sin integración Git, registrar la aceptación del entregable sin inventar un estado `merged`, conforme a [LIFECYCLE.md](LIFECYCLE.md#flujo-de-integración). La referencia de integración es un metadato complementario, nunca el mecanismo de reconstrucción del estado.

## 8. Cerrar y dar continuidad

1. [actor: human | agent] cierra las TASK que cumplen sus criterios, respetando su alcance parcial o completo y verificando que cada RFC de su alcance esté en `done`.
2. [actor: human | agent] cierra la RFC solo cuando todo su alcance satisface [LIFECYCLE.md](LIFECYCLE.md) y cada acción de su alcance está en `completed`.
3. [actor: human | agent] detecta el descendiente que no alcanza su éxito y solicita decisión: [actor: human] cancela el padre o reduce su alcance conforme a [PROJECT_STATE.md](PROJECT_STATE.md#regla-de-consistencia-entre-niveles).
4. [actor: human | agent] comprueba el proyecto con `hactors validate` antes de dar por terminada la operación.
5. [actor: human] autoriza el cierre de TASK y de WORKFLOW; ningún agente lo ejecuta de forma autónoma.
6. [actor: human] consolida el resumen del workflow_run y el de cada RFC que no sea RFC-D, conforme a [SUMMARY.md](SUMMARY.md).
7. [actor: human | agent] informa entregables, comprobaciones, limitaciones y decisiones pendientes sin reescribir la evidencia histórica.
8. [actor: human | agent] puede proponer trabajo adicional mediante otra RFC; no lo incorpora automáticamente al alcance cerrado.

No hay índice ni archivo que actualizar: una RFC cerrada permanece en `rfcs/` y su estado se lee de ella y de su árbol de instancias.
Los trabajos exclusivamente documentales o de análisis aplican estas responsabilidades a sus propios entregables y comprobaciones; no simulan compilaciones ni pruebas ajenas a su alcance.

## Puntos de intervención

Estas actuaciones son exclusivas de [actor: human]; [actor: agent] las propone y nunca las produce por su propia iniciativa. Sus condiciones están en la norma citada, no aquí.

| Intervención | Norma |
|---|---|
| Admitir una propuesta y aprobar alcance, contratos y criterios. | [LIFECYCLE.md](LIFECYCLE.md#rfc) |
| Autorizar el cierre de una TASK y de un WORKFLOW. | [PROJECT_STATE.md](PROJECT_STATE.md#propiedad-del-estado) |
| Aprobar la revisión, validar el resultado e integrarlo cuando aplique. | [LIFECYCLE.md](LIFECYCLE.md#flujo-de-integración) |
| Adoptar un cambio de diseño descubierto durante la ejecución. | [LIFECYCLE.md](LIFECYCLE.md#iteraciones-y-agregación) |
| Cancelar, abortar o reducir un alcance. | [PROJECT_STATE.md](PROJECT_STATE.md#regla-de-consistencia-entre-niveles) |
| Decidir `wont-fix` sobre un hallazgo y modificar su severidad cuando afecta el alcance aprobado. | [FINDING.md](FINDING.md) |
| Consolidar un resumen y reabrirlo. | [LIFECYCLE.md](LIFECYCLE.md#summary) |
| Aprobar un punto de decisión de un PLAN. | [PLAN_TEMPLATE.md](templates/PLAN_TEMPLATE.md#relación-con-decisiones) |
| Aprobar una excepción y autorizar una migración de datos existentes. | [EXCEPTIONS.md](EXCEPTIONS.md), [VERSIONING.md](VERSIONING.md) |
| Declarar la trivialidad de un cambio y aprobar su ejecución. | [TRIVIAL.md](TRIVIAL.md) |

Una etiqueta de actor no sustituye las autorizaciones de la tarea ni los permisos de las herramientas; las obligaciones particulares del ejecutor automatizado están en [AI.md](AI.md).

El registro observado de estas fases vive en el manifiesto del workflow_run, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#bloque-2-global_state). Los identificadores `step_XXX` y su correspondencia con estas fases los fija cada versión publicada, conforme a [templates/WORKFLOW_TEMPLATE.md](templates/WORKFLOW_TEMPLATE.md#correspondencia-con-las-fases).

## Vía rápida para cambios triviales

Los cambios de bajo impacto —corrección de enlaces, erratas, actualización de rutas— pueden seguir la vía rápida de [TRIVIAL.md](TRIVIAL.md) en lugar del flujo completo.

La vía rápida omite WORKFLOW, TASK y RFC; requiere declaración de trivialidad por [actor: human], reconocimiento previo obligatorio y aprobación antes de ejecutar. Si el reconocimiento revela alcance no trivial, el cambio se canaliza por el flujo completo y el identificador `TRV-nnnnn` no se reutiliza.
