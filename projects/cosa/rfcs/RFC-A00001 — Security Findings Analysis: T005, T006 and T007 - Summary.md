---
artifact: 'rfcs/RFC-A00001 — Security Findings Analysis: T005, T006 and T007.md'
title: Análisis de los tres hallazgos de seguridad y plan de corrección en tres fases
level: rfc
status: in-progress
final_state: under_review
target_state: done
date: '2026-11-04'
---

Estructura y secciones: `specs/templates/SUMMARY_TEMPLATE.md`. Reglas y niveles: `specs/SUMMARY.md`.
Este resumen sintetiza y referencia; no reproduce el informe ni la RFC que resume.

## Estado final

El estado justificable es `under_review`: el informe existe, sus ocho criterios se comprobaron contra
él y la revisión de [actor: human] no consta registrada, así que no puede afirmarse `validated` ni
`done`. FND-00001, `critical`, sigue `open` y bloquea el cierre de la TASK de origen, no el estado de
esta RFC.

| Criterio | Estado | Evidencia |
|---|---|---|
| C1 — los doce apartados de la orden de trabajo | Satisfecho | `EVD-00004` |
| C2 — matriz de trazabilidad de siete columnas | Satisfecho | `EVD-00004` |
| C3 — cada causa raíz con su evidencia y su componente | Satisfecho | `EVD-00004` |
| C4 — plan por fases con los once apartados cada una | Satisfecho | `EVD-00004` |
| C5 — alternativas evaluadas y selección motivada | Satisfecho | `EVD-00004` |
| C6 — información insuficiente declarada, no inferida | Satisfecho | `EVD-00004` |
| C7 — sin código de producción, sin tests, sin commits de implementación | Satisfecho | `EVD-00004` |
| C8 — ningún hallazgo cerrado solo porque su test pueda hacerse pasar | Satisfecho en el análisis; ver la limitación sobre FND-00004 | `EVD-00004` |

## Objetivo y alcance

Reconstruir los tres hallazgos demostrados por `RFC-T00005`, `RFC-T00006` y `RFC-T00007`, trazarlos
hasta el código de producción que los permite, correlacionarlos para fijar un orden de corrección que
no duplique soluciones, y producir un plan por fases. Los ocho objetivos G1–G8 y las tres exclusiones
deliberadas están en la RFC; no se repiten aquí.

El alcance es documental: esta RFC no corrige nada. Las correcciones viven en sus tres RFC derivadas,
cada una con su resumen autónomo.

## Resultados alcanzados

| Resultado | Referencia |
|---|---|
| Cuatro causas raíz con su componente responsable y su evidencia, sin dar por supuesto que el componente que detecta es el que debe corregir | `root_causes` RC-1–RC-4 en la RFC |
| Matriz de trazabilidad RFC-Txxx → hallazgo → causa raíz → componente → corrección → tests → fase | Sección «Matriz de trazabilidad» del informe |
| Orden de corrección en tres fases: contrato del consumidor, binding exclusivo de identidad, sujeto de sistema operativo acotado | `implementation_plan.phases`, y las tres RFC derivadas |
| Alternativas evaluadas por causa raíz con su selección motivada y su rechazo razonado | `alternatives_considered` en la RFC |
| Quince riesgos de implementación identificados con su mitigación | `risks` R1–R15 en la RFC |
| Siete hallazgos registrados: cuatro de los tests de origen y tres del propio análisis | `EVD-00004` y los registros `FND-00001`–`FND-00007` |

## Decisiones

No se creó ningún `ADR-nnnnn` para esta RFC. Las decisiones que adopta están registradas en ella y se
referencian allí, conforme a `specs/DECISIONS.md`: la selección por causa raíz en
`alternatives_considered`, los rechazos razonados que sostienen C8, y el orden de fases en
`implementation_plan`.

La decisión de despliegue y credenciales de la fase 3 —`gate_003` de `PLAN-00001`, que la RFC prevé
como paso 3.1— es de [actor: human] y no consta registrada; se declara en las limitaciones.

## Verificación

Esta RFC no produce código ni tests propios; su comprobación es documental. Las fases que sí produjo
quedan aquí con su estado, y cada una se detalla en su propio resumen.

| Comprobación o fase | Objetivo | Estado | Referencia |
|---|---|---|---|
| Comprobación documental de C1–C8 | Acreditar el informe contra sus ocho criterios | Satisfecha | `EVD-00004` |
| Fase 1 — contrato del consumidor | Cerrar FND-00002 y FND-00003 | Ejecutada, con la repetibilidad sin cumplir | `rfcs/RFC-A00001-F00001 — IPC Consumer-Side Contract Enforcement.md` |
| Fase 2 — binding exclusivo de identidad | Cerrar FND-00004 | Ejecutada, sin campaña de verificación propia | `rfcs/RFC-A00001-F00002 — Exclusive Identity-to-Connection Binding.md` |
| Fase 3 — auditoría del sujeto acotado | Decidir el modelo antes de implementar | Solo la auditoría; la implementación no llegó a iniciarse | `rfcs/RFC-A00001-A00001 — Bounded OS Subject: Architecture & Feasibility Audit.md` |

## Evidencias

| Evidencia | Afirmación que respalda |
|---|---|
| `EVD-00004` en `hactors/workflow_run_000001/task_run_000001/rfc_run_000001/` | El informe existe con sus doce apartados, su matriz y la baseline que declara; el análisis no tocó código |

Las evidencias de las fases no se listan aquí: pertenecen a los resúmenes de sus RFC derivadas.

## Hallazgos

| Hallazgo | Tipo | Severidad | Estado |
|---|---|---|---|
| `FND-00001` en `…/rfc_run_000001/test_run_000001/` | defect | critical | open |
| `FND-00002` en `…/rfc_run_000001/test_run_000002/` | defect | high | resolved |
| `FND-00003` en `…/rfc_run_000001/test_run_000002/` | defect | critical | resolved |
| `FND-00004` en `…/rfc_run_000001/test_run_000003/` | defect | critical | resolved |
| `FND-00005` en `…/rfc_run_000001/` | inconsistency | low | open |
| `FND-00006` en `…/rfc_run_000001/` | gap | low | open |
| `FND-00007` en `…/rfc_run_000001/` | inconsistency | low | open |

Las rutas abreviadas con `…` cuelgan de
`hactors/workflow_run_000001/task_run_000001/rfc_run_000001`. FND-00002, FND-00003 y FND-00004 se
detectaron en los `test_run` de las RFC de origen y se corrigieron en las fases 1 y 2; su estado
terminal lo acredita la evidencia de cada fase, no este resumen.

## Limitaciones y cuestiones pendientes

- **FND-00001 sigue abierto y no tiene acción que lo trate.** La fase que debía cerrarlo no llegó a
  implementarse: los pasos 4 a 8 de `PLAN-00001` no se iniciaron y el documento real de esa fase,
  `docs/analisis/tests/RFC-T010 — Implementation of OS Process Confinement.md`, está vacío —cero
  bytes—. Lo cierra una RFC de implementación del confinamiento que aún no existe.
- **FND-00004 se resolvió sin secuencia causal.** La resolución se apoya en la lectura del código que
  hizo la auditoría y en que las dos pruebas de identidad pasan verdes en ambos árboles, no en
  revertir el cambio de producción y reproducir el fallo original, que es lo que C8 de
  `RFC-A00001-F00002` pide. `ACT-00009`, la campaña dedicada, sigue `pending`.
- **Baseline contradictoria entre dos fuentes del corpus.** El informe declara vigente 110/113 Ninja y
  107/110 Makefiles citando el Summary de RFC-T008 §8; el Summary de la fase 1 llama obsoleta esa
  misma cifra, atribuye el cambio a RFC-T008 y mide 129/132 y 126/129. La aritmética —de 113 a 132 y
  de 110 a 129— coincide con las entradas CTest que registró la fase 1, no con T008. Se registran las
  dos cifras atribuidas a su fuente y a su fecha; no se eligió una por inferencia, y no se abrió un
  octavo hallazgo porque los siete registrados son los del análisis real.
- **La corrección de la fase 1 sí está commiteada, contra lo que declara su propio Summary.** El
  Summary de `RFC-T006-F1` afirma que el trabajo quedó sin commitear en `dev`; la medición lo
  encuentra en el commit `e1f5d7d` del 2026-09-19, bajo un asunto —«tests for runtime module»— que no
  lo describe. De los dieciocho ficheros que cambia ese commit, trece son exactamente los once
  modificados y dos nuevos que declara el Summary, y las 38 líneas borradas coinciden; los otros cinco
  son tests y documentación del módulo runtime. Por eso `EVD-00005` lleva `source.commit` vacío: la
  revisión examinada fue un árbol de trabajo sin commitear, y afirmar ese hash como examinado sería
  falso.
- **FND-00005, FND-00006 y FND-00007 no declaran afectados.** Los documentos que los originan —
  `docs/security.md`, el filtro seccomp del worker confinado y los sumarios del repositorio COSA— no
  son artefactos de este proyecto HACTORS, así que no hay destino resoluble para su `affects`. Es una
  limitación del modelo, no una omisión.
- **Los resúmenes de `RFC-T00005`, `RFC-T00006` y `RFC-T00007` no existen.** `specs/RFC.md` exige un
  resumen asociado a toda RFC que no sea RFC-D; esas tres se registraron como origen de este análisis
  y su ejecución pertenece a sus propias instancias históricas, no a este `workflow_run`.
- **Plataforma y comandos ausentes en cuatro evidencias.** Los sumarios reales de T005, T006, T007 y de
  la fase 1 registran retornos y resultados por caso, pero ninguno declara la plataforma, y los de T006
  y la fase 1 tampoco los comandos literales. `EVIDENCE.md` exige ambos; se dejaron vacíos en lugar de
  reconstruirlos por analogía con los sumarios vecinos. Solo la auditoría declara su host, y por eso
  `EVD-00006` y `EVD-00007` sí lo llevan.
- **Fechas de este resumen.** Está fechado el 2026-11-04, que es cuando se redacta, sobre una
  ejecución de septiembre de 2026. `status: in-progress`: ninguna de las RFC que participan es
  terminal, así que ninguna consolida su resumen.

## Matriz de trazabilidad

| Objetivo | Criterio | Evidencia | Estado |
|---|---|---|---|
| G1, G2, G3, G4, G5, G6, G7, G8 | C1 | `EVD-00004` | Satisfecho |
| G2, G4, G6 | C2 | `EVD-00004` | Satisfecho |
| G2, G3 | C3 | `EVD-00004` | Satisfecho |
| G6 | C4 | `EVD-00004` | Satisfecho |
| G5 | C5 | `EVD-00004` | Satisfecho |
| G8 | C6 | `EVD-00004` | Satisfecho |
| G1–G8 | C7 | `EVD-00004` | Satisfecho |
| G5, G7 | C8 | `EVD-00004` | Satisfecho en el análisis; FND-00004 se resolvió después sin secuencia causal |

## Historial de ejecuciones

| Instancia | Motivo | Estado inicial | Trabajo realizado | Artefactos | Evidencias y hallazgos | Resultado | Estado final |
|---|---|---|---|---|---|---|---|
| `rfc_run_000001` | Ejecutar el análisis de los tres hallazgos y producir el informe | `pending` | Informe de doce apartados, matriz de trazabilidad, cuatro causas raíz, plan en tres fases y registro de los siete hallazgos | `PLAN-00001` y las tres RFC derivadas, por relación `derives` | `EVD-00004`; `FND-00005`, `FND-00006` y `FND-00007` abiertos aquí | Análisis completado; ninguna corrección, conforme a C7 | `completed` |
| `rfc_run_000001/test_run_000001` | Reproducir la propiedad de `TEST-00001` sobre el escenario de `RFC-T00005` | `pending` | Ejecución en ambos árboles con veinte repeticiones por árbol | `tests/TEST-00001.md` | `EVD-00001`; `FND-00001` | Bypass observado: el recurso protegido se elimina tras la denegación | `completed` |
| `rfc_run_000001/test_run_000002` | Reproducir la propiedad de `TEST-00002` sobre el escenario de `RFC-T00006` | `pending` | Ejecución en ambos árboles con veinte repeticiones por árbol | `tests/TEST-00002.md` | `EVD-00002`; `FND-00002` y `FND-00003` | Siete casos verdes y tres rojos reproducibles | `completed` |
| `rfc_run_000001/test_run_000003` | Reproducir la propiedad de `TEST-00003` sobre el escenario de `RFC-T00007` | `pending` | Ejecución en ambos árboles con veinte repeticiones por árbol, y re-medición sobre el árbol con T008 | `tests/TEST-00003.md` | `EVD-00003`; `FND-00004` | Cuatro casos verdes y el caso histórico en rojo | `completed` |
| `rfc_run_000001/plan_run_000001` | Ejecutar la secuencia de `PLAN-00001` | `pending` | Pasos 1 a 3, que son las tres RFC derivadas; los pasos 4 a 8 no se iniciaron | `plans/PLAN-00001 — Corrección secuenciada de los hallazgos T005, T006 y T007.md` | Las evidencias y hallazgos de los tres `rfc_run` hijos | Secuencia incompleta: `gate_003` sin decisión registrada | `blocked` |
| `…/plan_run_000001/rfc_run_000002` | Ejecutar la fase 1 | `pending` | Corrección del contrato en el consumidor y sus pruebas | `RFC-A00001-F00001` | `EVD-00005`; cierra `FND-00002` y `FND-00003` | Corrección integrada en `e1f5d7d`; repetibilidad no cumplida | `in_progress` |
| `…/rfc_run_000002/test_run_000004` | Verificar la fase 1 contra `TEST-00002` | `pending` | Medición del test de contrato y de las suites completas | `tests/TEST-00002.md` | `EVD-00005` | 10/10 en el test de contrato; el agotamiento de `ThreadPoolExecutorTest` impide acreditar la repetibilidad | `completed` |
| `…/plan_run_000001/rfc_run_000003` | Ejecutar la fase 2 | `pending` | Binding exclusivo de identidad en `IPCManager` y su prueba | `RFC-A00001-F00002` | `EVD-00006`; cierra `FND-00004` | Integrado en `1d58d53`; sin campaña de verificación propia | `in_progress` |
| `…/rfc_run_000003/test_run_000005` | Verificar la fase 2 contra `TEST-00003` | `pending` | Medición indirecta por la auditoría sobre la revisión `1d58d53` | `tests/TEST-00003.md` | `EVD-00006` | Las dos pruebas de identidad verdes en ambos árboles | `completed` |
| `…/plan_run_000001/rfc_run_000004` | Ejecutar la fase 3 en su alcance de auditoría | `pending` | Auditoría de arquitectura y viabilidad del sujeto acotado, con su paquete de evidencia | `RFC-A00001-A00001` | `EVD-00007`; `FND-00001` confirmado abierto | Auditoría completada; la implementación no se inició | `completed` |
| `…/rfc_run_000004/test_run_000006` | Comprobar `TEST-00001` sobre la revisión auditada | `pending` | Selección CTest de doce entradas por árbol | `tests/TEST-00001.md` | `EVD-00007` | 11/12 en cada árbol; el único fallo es el caso T005 | `completed` |

## Artefactos de origen

| Artefacto | Ruta relativa al proyecto |
|---|---|
| La RFC resumida | `rfcs/RFC-A00001 — Security Findings Analysis: T005, T006 and T007.md` |
| La TASK declarada en `identity.task_ref` | `tasks/TASK-00001.md` |
| Las RFC derivadas | Solo como relación `derives`: `RFC-A00001-F00001`, `RFC-A00001-F00002` y `RFC-A00001-A00001`, cada una con su resumen autónomo |
| El plan que secuencia las fases | `plans/PLAN-00001 — Corrección secuenciada de los hallazgos T005, T006 y T007.md` |
| Las RFC de origen de los tres hallazgos | `rfcs/RFC-T00005 …`, `rfcs/RFC-T00006 …` y `rfcs/RFC-T00007 …`, por relación `informs` hacia esta RFC |

