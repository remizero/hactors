---
artifact: rfcs/RFC-A00001-F00001 — IPC Consumer-Side Contract Enforcement.md
title: 'Fase 1: el consumidor rechaza el contrato malformado antes de la admisión'
level: rfc
status: in-progress
final_state: draft
target_state: done
date: '2026-11-04'
---

Estructura y secciones: `specs/templates/SUMMARY_TEMPLATE.md`. Reglas y niveles: `specs/SUMMARY.md`.
Este resumen sintetiza y referencia; no reproduce la RFC ni el sumario real que la origina.

## Estado final

El estado justificable es `draft`, por dos razones independientes. La documental: `draft → approved`
es una transición de [actor: human] que no consta registrada, y HACTORS separa el estado documental
del de ejecución, así que el trabajo observado vive en su `rfc_run` y no en este campo. La material:
C7 no se cumple y `ACT-00005` sigue `pending`. No hay ningún hallazgo `critical` ni `high` en `open`
que bloquee: los dos que esta RFC cierra están `resolved`.

| Criterio | Estado | Evidencia |
|---|---|---|
| C1 — el decoder rechaza operación vacía, bytes de control y bytes altos, y acepta la válida y la máxima imprimible | Satisfecho | `EVD-00005` |
| C2 — los dos extractores aceptan únicamente un NUL real y rechazan control, alto y cola sin terminador | Satisfecho | `EVD-00005` |
| C3 — routing ausente y NUL inicial conservan el fallback canónico | Satisfecho | `EVD-00005` |
| C4 — los rechazos nuevos se traducen a contrato malformado, con registro estructurado y contador del endpoint destinatario | Satisfecho | `EVD-00005` |
| C5 — el test de seguridad del contrato pasa 10/10 en ambos árboles sin modificar los intocables | Satisfecho | `EVD-00005` |
| C6 — ningún verde perdido en las suites completas y ningún rojo nuevo | Satisfecho | `EVD-00005` |
| C7 — resultado reproducible con orden aleatorio y semilla fija en ambos árboles | **No satisfecho** para el conjunto completo; sí para las suites propias | `EVD-00005` |
| C8 — causalidad demostrada revirtiendo y restaurando la corrección | Satisfecho, con tres controles de tres | `EVD-00005` |

## Objetivo y alcance

Trasladar la garantía del contrato wire del productor al consumidor, que es quien posee la frontera
por la que entra, con dos puntos de enforcement y ningún tercero: la validación del cuerpo en el
decoder y el endurecimiento de cada extractor de enrutamiento en su propia ruta. Los seis objetivos
G1–G6 y las cuatro exclusiones deliberadas están en la RFC y no se repiten aquí; entre ellas, el
extractor compartido y todo lo relativo a T005, T007 y `IPCManager`.

## Resultados alcanzados

| Resultado | Referencia |
|---|---|
| El decoder aplica el validador de operación ya existente sobre la vista prestada, sin copias ni asignaciones y sin segunda implementación | `ACT-00001` |
| Los dos extractores de producción devuelven un opcional cuya ausencia significa malformado, de modo que éxito implica terminación con NUL real | `ACT-00002` |
| Una faceta descubrible notifica el rechazo ya decidido, con un único código compartido; el endpoint conserva su validación y su decisión | `ACT-00003` |
| Cincuenta y siete casos nuevos en cuatro suites propietarias, todos a través de superficies públicas | `ACT-00004` |
| El test de seguridad del contrato pasó de 7/10 a 10/10 con los nueve archivos intocables de hash idéntico | `EVD-00005` |
| Las suites completas pasaron de 129/132 a 131/133 en Ninja y de 126/129 a 128/130 en Makefiles, con los dos rojos restantes idénticos a los de la baseline | `EVD-00005` |
| Los tres controles causales se reprodujeron en ambos árboles, con restauración byte a byte y diff limpio | `EVD-00005` |
| `FND-00002` y `FND-00003` cerrados en el consumidor | Sus registros en `…/test_run_000002/` |

La forma del cambio, archivo por archivo, está en el sumario real que la RFC lista en `references`;
no se transcribe aquí.

## Decisiones

No se creó ningún `ADR-nnnnn`. Las decisiones están registradas en la RFC y se referencian allí: las
tres alternativas con su rechazo razonado en `alternatives_considered`, y el reparto de
responsabilidad en `ownership_changes`.

Dos decisiones de [actor: human] faltan y se declaran en las limitaciones: la aceptación de la
desviación sobre la repetibilidad global, que corresponde a `gate_001` de `PLAN-00001`, y el avance
del estado documental de esta RFC.

## Verificación

| Comprobación o fase | Objetivo | Estado | Referencia |
|---|---|---|---|
| Unitarias del decoder y de cada extractor en su módulo | C1, C2, C3 | Satisfecha | `ACT-00004` |
| Integración de las dos rutas por separado con un frame real por socketpair | C2, C3, C4 | Satisfecha | `ACT-00004` |
| Prueba de contrato con el endpoint y el gestor de IPC reales | C4 | Satisfecha | `ACT-00004` |
| Test de seguridad del contrato, intocable | C5 | Satisfecha, 10/10 | `tests/TEST-00002.md` |
| Suites completas de los dos árboles frente a su baseline | C6 | Satisfecha | `tests/TEST-00002.md` |
| Veinte repeticiones en orden aleatorio con semilla fija | C7 | No satisfecha para el conjunto completo | `EVD-00005` |
| Tres controles causales con reversión y restauración | C8 | Satisfecha | `EVD-00005` |

Ningún `HRN-nnnnn` participa: este proyecto no registra harness y las ejecuciones usan los binarios
de prueba de los dos árboles de construcción.

## Evidencias

| Evidencia | Afirmación que respalda |
|---|---|
| `EVD-00005` en `hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001/rfc_run_000002/test_run_000004/` | El resultado medido de las cuatro suites propias, del test de contrato, de las suites completas, de la repetibilidad y de los tres controles causales |

Es la única evidencia de esta RFC y verifica sus ocho criterios; que C7 conste como verificado no
significa que sea satisfactorio, conforme a `specs/EVIDENCE.md`.

## Hallazgos

| Hallazgo | Tipo | Severidad | Estado |
|---|---|---|---|
| `FND-00002` en `…/rfc_run_000001/test_run_000002/` | defect | high | resolved |
| `FND-00003` en `…/rfc_run_000001/test_run_000002/` | defect | critical | resolved |

Las rutas abreviadas con `…` cuelgan de `hactors/workflow_run_000001/task_run_000001`. Ambos se
detectaron en el `test_run` de `RFC-T00006`, anterior a esta RFC, y se resolvieron el 2026-09-18 con
las acciones de implementación y de prueba que aquí se referencian.

## Limitaciones y cuestiones pendientes

- **C7 no se cumple y la aceptación que lo cerraría no consta.** El requisito global de veinte
  repeticiones no se pudo acreditar porque una suite de ejecución enlazada agotó su techo de tiempo en
  ambos árboles; la suite tarda lo mismo en ejecución única que en la baseline, el módulo está fuera
  de este alcance y quedó intacto, y su causa no se estableció. `gate_001` de `PLAN-00001` es quien
  autoriza dar por cerrada la verificación con esa desviación declarada, y su decisión de
  [actor: human] no está registrada. Lo cierra establecer la causa en el módulo ajeno o la aceptación
  explícita del gate.
- **`ACT-00005` sigue `pending` con su entregable vacío.** Los addenda de esta fase en los documentos
  versionados que describen lo que se tocó no se escribieron; el listado concreto está en
  `documentation_impact` de la RFC. `ACT-00006` sí está `completed`, pero acredita la evidencia de la
  fase, no su documentación.
- **El criterio más estricto del documento real quedó incumplido por decisión del propietario.** Sus
  apartados 10 y 11 esperaban T005 como único rojo y T007 en verde; el criterio de la fase 1 en
  `RFC-A00001` espera esos dos rojos y sí se cumple en esa cláusula. La distinción y su consecuencia
  están en `consequences` de la RFC.
- **La baseline que declara la RFC está obsoleta y contradice a su origen.** Se declara en el resumen
  de `RFC-A00001` y no se repite aquí.
- **La corrección está integrada, contra lo que afirma el sumario real.** Ese sumario declara el
  trabajo sin commitear; la medición lo encuentra integrado en una revisión posterior bajo un asunto
  que no lo describe, y por eso `EVD-00005` lleva `source.commit` vacío: la revisión examinada fue un
  árbol de trabajo sin commitear. El detalle medido está en las limitaciones del resumen de
  `RFC-A00001`.
- **`status: in-progress`.** La RFC no es terminal, así que no consolida su resumen; declararlo
  `consolidated` corresponde a [actor: human].

## Matriz de trazabilidad

| Objetivo | Criterio | Evidencia | Estado |
|---|---|---|---|
| G1 | C1, C8 | `EVD-00005` | Satisfecho |
| G2 | C2, C8 | `EVD-00005` | Satisfecho |
| G3 | C3 | `EVD-00005` | Satisfecho |
| G4 | C4 | `EVD-00005` | Satisfecho |
| G5 | C5, C7 | `EVD-00005` | C5 satisfecho; C7 no, por la repetibilidad global |
| G6 | C6, C7 | `EVD-00005` | C6 satisfecho; C7 no, por la repetibilidad global |

## Historial de ejecuciones

| Instancia | Motivo | Estado inicial | Trabajo realizado | Artefactos | Evidencias y hallazgos | Resultado | Estado final |
|---|---|---|---|---|---|---|---|
| `rfc_run_000002` | Ejecutar la fase 1 del plan | `pending` | Endurecimiento del decoder y de los dos extractores, faceta nueva de notificación del rechazo y sus pruebas | `ACT-00001`–`ACT-00004` y `ACT-00006` completadas; `ACT-00005` pendiente | `EVD-00005` | Los dos hallazgos de contrato cerrados; la documentación versionada pendiente | `in_progress` |
| `rfc_run_000002/test_run_000004` | Verificar la fase contra `TEST-00002` | `pending` | Cuatro suites propias, el test de contrato, las suites completas de los dos árboles, veinte repeticiones y tres controles causales | `tests/TEST-00002.md` | `EVD-00005`; cierra `FND-00002` y `FND-00003` | 10/10 en el test de contrato y ningún verde perdido; la repetibilidad global sin cumplir | `completed` |

Las rutas abreviadas cuelgan de
`hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001`. `rfc_run_000002` no
está `completed` porque su RFC no es terminal y le queda una acción pendiente.

## Artefactos de origen

| Artefacto | Ruta relativa al proyecto |
|---|---|
| La RFC resumida | `rfcs/RFC-A00001-F00001 — IPC Consumer-Side Contract Enforcement.md` |
| La TASK declarada en `identity.task_ref` | `tasks/TASK-00001.md`, a través de `hactors/workflow_run_000001/manifest.yaml` |
| El plan que contrata esta fase en su `step_001` | `plans/PLAN-00001 — Corrección secuenciada de los hallazgos T005, T006 y T007.md` |
| La RFC de la que deriva | `rfcs/RFC-A00001 — Security Findings Analysis: T005, T006 and T007.md`, por relación `derives` |
| El TEST que fija la propiedad verificada | `tests/TEST-00002.md` |
| Las RFC que dependen de ésta | `rfcs/RFC-A00001-F00002 …` y `rfcs/RFC-A00001-A00001 …`, por relación `depends-on`; cada una con su resumen autónomo |
| El sumario real que origina el registro | Fuera del proyecto, en `references` de la RFC; no es un artefacto HACTORS |
