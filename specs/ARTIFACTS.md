# Artefactos.

un artefacto puede tener identidad propia y al mismo tiempo relacionarse con cero, uno o varios artefactos.

Este documento fija la autoridad de las fuentes y su conservación. La identidad y la nomenclatura están en [DEFINITIONS.md](DEFINITIONS.md#nomenclatura); los estados y sus transiciones, en [LIFECYCLE.md](LIFECYCLE.md) y en la plantilla de cada artefacto; la disposición física, en [PROJECTS.md](PROJECTS.md#estructura-de-un-proyecto-hactors); y el grafo, en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relaciones-del-proyecto).

## Tipos de Artefactos.

* WORKFLOW — [proceso versionado que ordena fases y pasos](WORKFLOW.md#identidad-y-versiones)
* TASK — [artefacto iniciador](HACTORS_SYSTEM.md#7-task-artefacto-iniciador)
* RFC — [convenciones de identidad y contenido](RFC.md)
* DECISION — [registro de una decisión](DECISIONS.md)
* PLAN — [decisión secuencial](DECISIONS.md#plan-y-decisión-secuencial)
* TEST — [propiedad bajo verificación](TESTS.md)
* HARNESS — [receta de verificación versionada](HARNESS.md)
* EVIDENCE — [registro de un hecho observado](EVIDENCE.md)
* FINDING — [registro de un defecto observado](FINDING.md)
* SUMMARY — [síntesis del resultado de un artefacto](SUMMARY.md)
* WORKFLOW_RUN
* TASK_RUN
* RFC_RUN
* PLAN_RUN
* TEST_RUN
* HARNESS_RUN — [instancia de uso de una versión de HARNESS](HACTORS_SYSTEM.md#12-harness_run-ejecución-de-una-versión-de-harness)

Las seis últimas son instancias de ejecución, no documentos: su jerarquía, su manifiesto y su estado observado se definen en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md).

## Autoridad

Cada artefacto es autoritativo sobre lo que su propia especificación le asigna, y sobre nada más. Un dato vive en un único campo autoritativo y los demás lo referencian sin redefinirlo.

| Prevalece | Sobre | Conforme a |
|---|---|---|
| La norma de `specs/`. | El `standards/` de un proyecto. | [STANDARDS.md](STANDARDS.md) |
| El documento aprobado. | El grafo que lo representa. | [RELATIONSHIPS.md](RELATIONSHIPS.md#consistencia) |
| El artefacto persistido. | Cualquier vista derivada de él. | [VIEWS.md](VIEWS.md) |
| La evidencia registrada. | La declaración de cumplimiento. | [EVIDENCE.md](EVIDENCE.md) |
| El estado observado de una instancia. | El resumen que la sintetiza. | [SUMMARY.md](SUMMARY.md#reconstrucción) |
| El contenido original de una RFC. | Su reescritura posterior. | [RFC.md](RFC.md#modificadores) |

Ninguna fuente se corrige en silencio. Una contradicción se declara y se resuelve por decisión registrada conforme a [DECISIONS.md](DECISIONS.md) o, cuando es un defecto de lo observado, por hallazgo conforme a [FINDING.md](FINDING.md).

## Conservación

- Los artefactos rechazados, cancelados o sustituidos no se eliminan por defecto, conforme a [LIFECYCLE.md](LIFECYCLE.md#rechazo-sustitución-y-cancelación).
- Un identificador consumido no se reutiliza aunque el artefacto no llegue a existir.
- La sustitución enlaza las dos versiones en ambos sentidos; no se mantienen dos vigencias contradictorias.
- Lo observado no se reescribe: la evidencia y los hallazgos conservan el contexto de su observación aunque desaparezca lo que los produjo.
- La historia no es estado vigente: conservar un artefacto terminal no autoriza a presentarlo como el estado actual, conforme a [PROJECT_STATE.md](PROJECT_STATE.md#historial).

## Restricciones

- No deducir autoridad del tipo de artefacto, de su ubicación ni de su antigüedad.
- No citar un artefacto como fuente de un dato cuya autoridad pertenece a otro.
- No resolver una contradicción eligiendo una interpretación sin registrarla.
- No reconstruir el estado desde una vista, un resumen ni el historial de versiones: se acredita desde los artefactos persistidos, conforme a [TRANSACTIONS.md](TRANSACTIONS.md#reconciliación).
