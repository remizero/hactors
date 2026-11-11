# Participación de agentes de IA

## Alcance

Este documento contiene únicamente las obligaciones particulares de `[actor: agent]`.
Los fundamentos y el proceso comunes están en [FOUNDATIONS.md](FOUNDATIONS.md) y [WORKFLOW.md](WORKFLOW.md); las etiquetas de actor se definen en [DEFINITIONS.md](DEFINITIONS.md#actores).
No establece un flujo alternativo ni restringe a [actor: human] las acciones que también puede ejecutar.

## Autoridad

- Ejecutar el alcance autorizado; no convertir una propuesta propia en una decisión aprobada.
- Consultar [LIFECYCLE.md](LIFECYCLE.md) antes de cambiar un estado, y [PROJECT_STATE.md](PROJECT_STATE.md#transiciones-de-una-acción) cuando la transición sea de una acción derivada.
- Una etiqueta de actor no sustituye las autorizaciones de la TASK ni los permisos de las herramientas.
- Si se requiere una intervención humana, detener la acción afectada y presentar la decisión pendiente; los puntos reservados a [actor: human] están enumerados en [WORKFLOW.md](WORKFLOW.md#puntos-de-intervención).
- Proponer cambios de diseño cuando sea necesario, sin aplicarlos como ajustes incidentales de implementación.

## Contexto y supuestos

- Resolver la carga conforme a [CONTEXT_LOADING.md](CONTEXT_LOADING.md), incluidas sus dependencias obligatorias.
- No tratar un enlace, un índice, un resumen o una vista generada como si se hubiera leído el contrato completo.
- No sustituir documentación vigente por recuerdos, conversaciones anteriores o convenciones inferidas.
- Si falta una fuente necesaria, informar su identidad y qué parte del trabajo bloquea; el bloqueo se registra en el `blocked_reason` de la instancia afectada, conforme a [WORKFLOW.md](WORKFLOW.md#4-verificar).
- Ante una contradicción, declararla y detener la parte afectada; no elegir silenciosamente una interpretación. El estado se lee del propio artefacto y de su árbol de instancias, no de una vista derivada de [VIEWS.md](VIEWS.md).
- Comunicar antes de implementarlas las decisiones que el contrato no determina y que afectan alcance, comportamiento o compatibilidad.

## Ejecución y entrega

- Corregir fallos propios dentro del alcance; no ampliar el trabajo para resolver fallos ajenos sin autorización.
- Preservar cambios del usuario y trabajo no relacionado.
- Informar archivos afectados, supuestos y resultados verificables; distinguir pruebas ejecutadas, omitidas y bloqueadas.
- No declarar una comprobación realizada cuando solo se ha escrito el comando o previsto su ejecución.
- Mantener la relación entre criterios y evidencia conforme a [TESTS.md](TESTS.md) y [EVIDENCE.md](EVIDENCE.md); lo que contradice un criterio se registra como hallazgo conforme a [FINDING.md](FINDING.md), no se corrige en silencio ni se descarta.
- Aplicar las mismas condiciones de aceptación que un ejecutor humano.

## Instrucciones de trabajo

[actor: human | agent] redacta las instrucciones para un agente mediante [PROMPTING.md](PROMPTING.md).
El rol descrito en una instrucción orienta el trabajo, pero no concede autoridad para aprobar ni integrar cambios.
