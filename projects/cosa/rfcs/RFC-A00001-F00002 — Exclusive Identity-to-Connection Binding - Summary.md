---
artifact: rfcs/RFC-A00001-F00002 — Exclusive Identity-to-Connection Binding.md
title: 'Fase 2: binding exclusivo entre identidad y descriptor activo'
level: rfc
status: in-progress
final_state: draft
target_state: done
date: '2026-11-04'
---

Estructura y secciones: `specs/templates/SUMMARY_TEMPLATE.md`. Reglas y niveles: `specs/SUMMARY.md`.
Este resumen sintetiza y referencia; no reproduce la RFC ni el informe de la auditoría.

## Estado final

El estado justificable es `draft`, y aquí la razón documental y la material se refuerzan. La
documental: `draft → approved` es de [actor: human] y no consta registrada, así que el trabajo
observado vive en su `rfc_run` y no en este campo. La material: de los ocho criterios solo seis están
acreditados por una evidencia registrada, y la campaña que acreditaría los dos restantes —`ACT-00009`—
sigue `pending` con su entregable vacío. `FND-00004`, `critical`, está `resolved`, así que no bloquea.

| Criterio | Estado | Evidencia |
|---|---|---|
| C1 — existe enforcement de exclusividad en el gestor del IPC bajo el lock de sesiones | Satisfecho | `EVD-00006` |
| C2 — una identidad no puede vincularse a dos descriptores activos y el duplicado se rechaza antes de conceder autoridad | Satisfecho | `EVD-00006` |
| C3 — el binding se libera al desconectar el propietario y un registro posterior se permite | Satisfecho | `EVD-00006` |
| C4 — dos identidades distintas conservan el comportamiento permitido | Satisfecho | `EVD-00006` |
| C5 — el binding existente sobrevive al rechazo del duplicado | Satisfecho | `EVD-00006` |
| C6 — sin estado de binding en la política estática, sin binding por PID y sin cambios de la fase 3 | **Sin acreditar** | Ninguna registrada |
| C7 — los tests protegidos intactos y el escenario histórico deja de ser reproducible | Satisfecho | `EVD-00006` |
| C8 — causalidad demostrada revirtiendo solo el cambio de producción | **Sin acreditar** | Ninguna registrada |

## Objetivo y alcance

Imponer la invariante de que, en cualquier instante, como máximo un descriptor activo representa una
identidad lógica dada, rechazando el registro duplicado antes de completar el registro y la
autorización, en un único punto de enforcement sobre el estado de peers y sesiones ya existente y bajo
el mismo lock que lo protege. Los seis objetivos G1–G6 y las cinco exclusiones están en la RFC; entre
las exclusiones, todo aislamiento de sistema operativo y la resolución de T005, que permanece abierto
después de esta fase.

## Resultados alcanzados

| Resultado | Referencia |
|---|---|
| La unicidad del binding identidad↔descriptor pasa de la allowlist de política a la tabla de peers, que ya opera bajo su lock | `ownership_changes` en la RFC |
| Un motivo de rechazo nuevo por identidad ya vinculada, con su línea de auditoría y su registro de traza en nivel de aviso | `ACT-00007` |
| Seis casos propios de la invariante, registrados como una única entrada de prueba | `ACT-00008` |
| La prueba de binding exclusivo y la de suplantación de identidad verdes en los dos árboles | `EVD-00006` |
| La comprobación ocurre bajo el lock de sesiones y la invariante se mantiene, leído sobre el código de la revisión examinada | `EVD-00006` |
| `FND-00004` cerrado como hallazgo de binding | Su registro en `…/test_run_000003/` |

El mecanismo concreto del cambio está en `ACT-00007` y en el informe de la auditoría, que la RFC lista
en `references`; no se transcribe aquí.

## Decisiones

No se creó ningún `ADR-nnnnn`. Las decisiones están en la RFC y se referencian allí: las cuatro
alternativas con su rechazo razonado en `alternatives_considered` —entre ellas el binding permanente
por PID y la reverificación en el endpoint, que es el criterio de no-cierre explícito— y el criterio de
no-cierre en `benefits.ai`.

El modelo de despliegue de un UID por servidor queda fuera de alcance por ser una decisión del
propietario; la contrata `gate_003` de `PLAN-00001`, que no consta decidida.

## Verificación

| Comprobación o fase | Objetivo | Estado | Referencia |
|---|---|---|---|
| Registro único, duplicado rechazado, identidades independientes, ciclo de vida del binding, supervivencia tras el rechazo y tentativas repetidas | C1, C2, C3, C4, C5 | Satisfecha por una entrada verde que ejecuta los seis casos | `tests/TEST-00003.md` |
| Selección focalizada de doce entradas en ambos árboles sobre la revisión examinada | C7 | Satisfecha, 11/12 en cada árbol | `tests/TEST-00003.md` |
| Lectura del punto de enforcement y de su lock en el código de producción | C1 | Satisfecha | `EVD-00006` |
| Revisión del cambio de producción y del árbol de trabajo | C6 | No ejecutada | `ACT-00009` |
| Secuencia causal con reversión del cambio de producción | C8 | No ejecutada | `ACT-00009` |
| Veinte repeticiones en orden aleatorio con semilla fija | Cierre de la fase 2 en `RFC-A00001` | No ejecutada | `ACT-00009` |

Ningún `HRN-nnnnn` participa. La verificación de esta fase no es propia: la aporta la auditoría de la
fase 3 al examinar el código, y esa mediación se declara en lugar de presentarla como una campaña
dedicada.

## Evidencias

| Evidencia | Afirmación que respalda |
|---|---|
| `EVD-00006` en `hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001/rfc_run_000003/test_run_000005/` | Que la corrección estaba implementada antes de la auditoría del 2026-09-20, que la comprobación vive bajo el lock de sesiones, y que las dos pruebas de identidad pasan verdes en ambos árboles |

Es evidencia indirecta y así se declara: acredita la existencia y el verde de la corrección, no la
secuencia causal que C8 exige.

## Hallazgos

| Hallazgo | Tipo | Severidad | Estado |
|---|---|---|---|
| `FND-00004` en `…/rfc_run_000001/test_run_000003/` | defect | critical | resolved |
| `FND-00001` en `…/rfc_run_000001/test_run_000001/` | defect | critical | open |

Las rutas abreviadas con `…` cuelgan de `hactors/workflow_run_000001/task_run_000001`. `FND-00004` se
detectó en el `test_run` de `RFC-T00007` y se resolvió el 2026-09-20 con `ACT-00007` y `ACT-00008`.
`FND-00001` no pertenece a esta RFC: figura aquí porque `EVD-00006` lo respalda al reproducir su fallo
sobre la revisión ya corregida, y porque esta fase lo deja explícitamente abierto.

## Limitaciones y cuestiones pendientes

- **C8 no se cumple y C6 no se acredita.** La secuencia causal completa —revertir solo el cambio de
  producción, reproducir el fallo original, restaurar y comprobar la identidad— no se llegó a ejecutar,
  y la revisión del cambio que C6 pide tampoco. Lo cierra `ACT-00009`, la campaña de verificación
  dedicada, que sigue `pending` con su entregable vacío aunque las dos acciones de las que depende
  estén `completed`.
- **`FND-00004` se resolvió sin secuencia causal.** Su `resolved` se apoya en que la corrección existe,
  en que su prueba propia pasa verde en ambos árboles y en la lectura del punto de enforcement bajo el
  lock, no en la reproducción del fallo original. `specs/FINDING.md` define `resolved` como acción
  completada y evidencia verificada, y eso se cumple en esa lectura estricta; la desviación respecto de
  C8 se declara aquí y en el «Resultado observado» de la RFC en lugar de reinterpretarse.
- **El cierre de la fase 2 en `RFC-A00001` se cumple solo en parte.** Su cláusula de test —5/5 en
  ambos árboles con los cuatro casos verdes anteriores intactos— sí está acreditada por la entrada
  verde que midió la auditoría. Las demás no: las suites completas no se ejecutaron, porque la
  auditoría midió una selección focalizada de doce entradas y su propio informe declara que no es un
  baseline; las veinte repeticiones aleatorias por árbol no se ejecutaron; y la limitación de
  atribución con su destino arquitectónico queda por escribir, que es lo que `documentation_impact` de
  la RFC señala.
- **Esta fase no tiene sumario real propio.** El documento real siguió en DRAFT, no fue editado y no
  produjo resumen, así que todo lo que aquí se afirma sobre su ejecución procede del informe de la
  auditoría posterior. Es la razón por la que la acreditación es indirecta.
- **T005 permanece abierto.** Conforme al alcance de la RFC: cerrar el binding no constituye aislamiento
  de sujeto de sistema operativo, y la fase 3 sigue siendo necesaria.
- **`status: in-progress`.** La RFC no es terminal, así que no consolida su resumen.

## Matriz de trazabilidad

| Objetivo | Criterio | Evidencia | Estado |
|---|---|---|---|
| G1 | C1, C2, C5 | `EVD-00006` | Satisfecho |
| G2 | C1, C2 | `EVD-00006` | Satisfecho |
| G3 | C3 | `EVD-00006` | Satisfecho |
| G4 | C4 | `EVD-00006` | Satisfecho |
| G5 | C6 | Ninguna | Sin acreditar |
| G6 | C7, C8 | `EVD-00006` | C7 satisfecho; C8 sin acreditar |

## Historial de ejecuciones

| Instancia | Motivo | Estado inicial | Trabajo realizado | Artefactos | Evidencias y hallazgos | Resultado | Estado final |
|---|---|---|---|---|---|---|---|
| `rfc_run_000003` | Ejecutar la fase 2 del plan | `pending` | Binding exclusivo bajo el lock de sesiones, con su motivo de rechazo, su auditoría y su traza | `ACT-00007` y `ACT-00008` completadas; `ACT-00009` pendiente | `EVD-00006` | La invariante implementada; la verificación dedicada sin registrar | `in_progress` |
| `rfc_run_000003/test_run_000005` | Verificar la fase contra `TEST-00003` | `pending` | Medición indirecta por la auditoría sobre la revisión examinada, con la prueba propia de la invariante y la de suplantación | `tests/TEST-00003.md` | `EVD-00006`; cierra `FND-00004` y respalda `FND-00001` | Las dos pruebas de identidad verdes en ambos árboles | `completed` |

Las rutas abreviadas cuelgan de
`hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001`. `rfc_run_000003` no está
`completed` porque su RFC no es terminal y le queda una acción pendiente.

## Artefactos de origen

| Artefacto | Ruta relativa al proyecto |
|---|---|
| La RFC resumida | `rfcs/RFC-A00001-F00002 — Exclusive Identity-to-Connection Binding.md` |
| La TASK declarada en `identity.task_ref` | `tasks/TASK-00001.md`, a través de `hactors/workflow_run_000001/manifest.yaml` |
| El plan que contrata esta fase en su `step_002` | `plans/PLAN-00001 — Corrección secuenciada de los hallazgos T005, T006 y T007.md` |
| La RFC de la que deriva | `rfcs/RFC-A00001 — Security Findings Analysis: T005, T006 and T007.md`, por relación `derives` |
| Su prerequisito declarado | `rfcs/RFC-A00001-F00001 — IPC Consumer-Side Contract Enforcement.md`, por relación `depends-on` |
| El TEST que fija la propiedad verificada | `tests/TEST-00003.md` |
| La RFC que la audita | `rfcs/RFC-A00001-A00001 — Bounded OS Subject: Architecture & Feasibility Audit.md`, con su resumen autónomo |
