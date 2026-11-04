---
artifact: hactors/workflow_run_000001
title: 'Ejecución de TASK-00001: análisis de los hallazgos T005, T006 y T007 y sus
  dos primeras fases de corrección'
level: workflow_run
status: in-progress
final_state: blocked
target_state: completed
date: '2026-11-04'
---

Estructura y secciones: `specs/templates/SUMMARY_TEMPLATE.md`. Reglas y niveles: `specs/SUMMARY.md`.
Este resumen sintetiza y referencia; no reproduce los artefactos que resume. Las tres RFC derivadas
tienen su propio resumen autónomo y sus resultados no se incorporan aquí: esta es la única instancia
donde las cuatro ejecuciones se ven juntas.

## Estado final

`final_state: blocked` reproduce `global_state.status` del manifiesto de la instancia y no se
reinterpreta. El motivo que ese manifiesto registra es doble: `step_008` de `WORKFLOW-00001@v001` es
[actor: human] y su aceptación no consta en ningún registro, y el alcance corregido no está completo.

Los criterios de aceptación de la TASK son los ocho de su RFC, y los ocho están satisfechos. Sus
títulos y su justificación uno a uno están en el resumen de `RFC-A00001`; no se copian aquí.

| Criterio | Estado | Evidencia |
|---|---|---|
| `RFC-A00001#C1` | Satisfecho | `EVD-00004` |
| `RFC-A00001#C2` | Satisfecho | `EVD-00004` |
| `RFC-A00001#C3` | Satisfecho | `EVD-00004` |
| `RFC-A00001#C4` | Satisfecho | `EVD-00004` |
| `RFC-A00001#C5` | Satisfecho | `EVD-00004` |
| `RFC-A00001#C6` | Satisfecho | `EVD-00004` |
| `RFC-A00001#C7` | Satisfecho | `EVD-00004` |
| `RFC-A00001#C8` | Satisfecho | `EVD-00004` |

Que los ocho estén satisfechos no cierra la ejecución. Esos criterios miden el análisis, que es
documental, y lo que impide el cierre es posterior a él:

| Condición que impide el cierre | Referencia |
|---|---|
| `FND-00001`, `critical`, en `open`: bloquea el cierre de la TASK donde se originó | `specs/FINDING.md`, y el registro junto a `test_run_000001` |
| `ACT-00005` y `ACT-00009` en `pending`, con su entregable vacío | campo `actions:` de `RFC-A00001-F00001` y de `RFC-A00001-F00002` |
| `gate_003` de `PLAN-00001` sin decisión registrada | `plans/PLAN-00001 — Corrección secuenciada de los hallazgos T005, T006 y T007.md` |
| `step_008` sin la aceptación de [actor: human] | bloque `review` del manifiesto, reproducido más abajo |

Las cuatro están escritas también en `execution.blockers` de `tasks/TASK-00001.md`.

## Objetivo y alcance

La TASK declarada en `identity.task_ref` pide registrar en HACTORS el análisis de seguridad que ya se
había realizado sobre el árbol real: la RFC de tipo A con su informe de doce apartados y su matriz de
trazabilidad, su resumen, los hallazgos y las evidencias del análisis como registros propios, las
instancias de ejecución con los estados observados y las aristas del grafo hacia las RFC derivadas y
las ejecuciones de los tests. Está en [tasks/TASK-00001.md](../../tasks/TASK-00001.md) y no se copia
aquí.

La ejecución la ordena `WORKFLOW-00001@v001` con sus nueve pasos, desde la resolución del contexto
hasta el cierre o la declaración explícita de la deuda que lo impide.

Dos límites de alcance conviene declarar:

- **Esta ejecución registra trabajo ya realizado; no lo produce.** Las observaciones proceden del
  corpus real del proyecto en `docs/analisis/` y de los resúmenes de sus tres tests de seguridad.
  Ningún artefacto de este proyecto modificó el árbol de COSA ni produjo un cambio de producción
  nuevo.
- **La implementación del confinamiento queda fuera.** Los pasos 3.1 a 3.5 del plan —`step_004` a
  `step_008` de `PLAN-00001`— no llegaron a iniciarse; de la fase 3 solo se ejecutó su auditoría, que
  por diseño no toca producción.

## Resultados alcanzados

| Resultado | Referencia |
|---|---|
| El análisis de los tres hallazgos quedó registrado como RFC de tipo A, con su informe y su resumen | `rfcs/RFC-A00001 — Security Findings Analysis: T005, T006 and T007.md` |
| Las tres correcciones que de él se derivan quedaron registradas como RFC propias, cada una con su resumen autónomo | relación `derives` en `manifest.yaml` |
| Las tres RFC de origen de los tests de seguridad quedaron registradas con su numeración real | `rfcs/RFC-T00005…`, `rfcs/RFC-T00006…`, `rfcs/RFC-T00007…` |
| Siete hallazgos y ocho evidencias registrados junto a su origen, con su tipo, su severidad y su estado | el directorio de cada instancia |
| El árbol de ejecución completo: un `workflow_run`, un `task_run`, cuatro `rfc_run`, un `plan_run` y seis `test_run` | `hactors/workflow_run_000001/` |
| La fase 1 ejecutada sobre el árbol real: `FND-00002` y `FND-00003` pasaron a `resolved` | el resumen de `RFC-A00001-F00001` |
| La fase 2 ejecutada sobre el árbol real: `FND-00004` pasó a `resolved` | el resumen de `RFC-A00001-F00002` |
| La fase 3 reducida a su auditoría: los modelos de alojamiento quedaron clasificados, sin decisión registrada ni cambio de producción | el resumen de `RFC-A00001-A00001` |
| El grafo del proyecto cerrado: 81 aristas registradas y `hactors validate` sin inconsistencias | `manifest.yaml` |

## Decisiones

No se creó ningún `ADR-nnnnn`: el contador `adr` sigue en 0. Las decisiones técnicas del trabajo
registrado viven en los artefactos que las adoptan y se referencian allí, conforme a
`specs/DECISIONS.md`: la selección por causa raíz y el orden de fases en `RFC-A00001`, y la secuencia
con sus cinco gates en `PLAN-00001`.

Las decisiones de [actor: human] que el plan exige y que **no constan registradas** son `gate_001` —la
autorización para dar por cerrada la verificación de la fase 1 con su repetibilidad global sin
cumplir—, `gate_003` —el modelo de alojamiento y credenciales de la fase 3, cuyo criterio de aprobación
exige además un ADR—, `gate_004` y `gate_005`, y la aceptación de `step_008`.

Cuatro decisiones de registro adoptó el propietario del proyecto para esta ejecución:

| Decisión | Qué se decidió y por qué |
|---|---|
| Identidad de las RFC de origen de los tests | Conservar la numeración real —`RFC-T00005`, `RFC-T00006`, `RFC-T00007`— en lugar de reasignar 1, 2 y 3, con `rfc_t: 7` por las siete que el corpus real declara. Acepta una brecha de conservación: cuatro identidades declaradas no tienen archivo. |
| Derivación de las RFC de corrección | Las tres derivan de `RFC-A00001`, que es la que produce el plan, y no de las RFC-T de origen. Los nombres históricos reales quedan anotados dentro de cada documento. |
| Severidad de los hallazgos | Por impacto y no por origen: tres `critical` y un `high` entre los cuatro defectos que midieron los tests. |
| Autoría de TEST y WORKFLOW | Redactados a mano, e incrementados a mano sus contadores, porque ninguna orden de la CLI crea esas dos familias. |

La primera establece una excepción técnica, y `specs/DECISIONS.md` pide un ADR para ella. El
propietario decidió asentarla como deuda en el libro de asientos de la herramienta —`TODO.md` en la
raíz de HACTORS, que no es un artefacto de este proyecto—; la desviación se declara en las
limitaciones en lugar de darse por buena.

## Verificación

Los nueve pasos del workflow con el estado observado que registra el manifiesto, y las fases que el
plan produjo. Un TEST se referencia por su archivo, no por su `test_run`.

| Comprobación o fase | Objetivo | Estado | Referencia |
|---|---|---|---|
| `step_001` a `step_007` de `WORKFLOW-00001@v001` | Desde la resolución del contexto hasta la solicitud de revisión | `completed` los siete | `global_state.steps` del manifiesto |
| `step_008` | Validar e integrar con la aceptación de [actor: human] | `pending` | bloque `review`, reproducido más abajo |
| `step_009` | Cerrar y dar continuidad | `pending` | depende de `step_008` |
| Fase 1 — contrato del consumidor (`step_001` del plan, `AC1`) | Cerrar `FND-00002` y `FND-00003` | Ejecutada; la cláusula de veinte repeticiones globales sin cumplir | `rfcs/RFC-A00001-F00001 — IPC Consumer-Side Contract Enforcement.md` |
| Fase 2 — binding exclusivo (`step_002` del plan, `AC2`) | Cerrar `FND-00004` | Ejecutada; sin campaña de verificación propia | `rfcs/RFC-A00001-F00002 — Exclusive Identity-to-Connection Binding.md` |
| Fase 3 — auditoría del sujeto acotado (`step_003` del plan, `AC3`) | Decidir el modelo antes de implementar | Ejecutada; sin cambio de producción ni commit | `rfcs/RFC-A00001-A00001 — Bounded OS Subject: Architecture & Feasibility Audit.md` |
| Pasos 3.1 a 3.5 (`step_004` a `step_008` del plan, `AC4` y `AC5`) | Implementar el confinamiento | No iniciados: el 3.1 es la decisión misma de `gate_003` y los cuatro restantes están bloqueados por ella | `plans/PLAN-00001 — Corrección secuenciada de los hallazgos T005, T006 y T007.md` |
| `tests/TEST-00001.md` | Reproducir el bypass del Executor | Ejecutado dos veces: rojo en la reproducción inicial y rojo otra vez sobre el árbol corregido | `EVD-00001`, `EVD-00007` |
| `tests/TEST-00002.md` | Medir el contrato wire en el consumidor | Ejecutado dos veces: tres fallos reproducibles antes de la fase 1 y 10/10 después | `EVD-00002`, `EVD-00005` |
| `tests/TEST-00003.md` | Medir la suplantación de identidad | Ejecutado dos veces: un fallo antes de la fase 2 y verde en los dos árboles después | `EVD-00003`, `EVD-00006` |

Ningún HARNESS intervino: el proyecto no declara ningún catálogo `HRN-nnnnn` —los contadores `harness`
y `harness_run` están en 0—, así que no se ejecutó ninguna receta y la verificación descansa
únicamente en evidencia de tipo `test-output`, `artifact` y `document`.

## Evidencias

Las ocho que el manifiesto lista en `integration.verification_refs`.

| Evidencia | Afirmación que respalda |
|---|---|
| `EVD-00001` en `…/rfc_run_000001/test_run_000001/` | T005 reproducido: la vía mediada deniega y el `unlink` directo elimina el recurso protegido |
| `EVD-00002` en `…/rfc_run_000001/test_run_000002/` | T006 reproducido: siete casos verdes y tres fallos reproducibles, con las suites completas medidas |
| `EVD-00003` en `…/rfc_run_000001/test_run_000003/` | T007 reproducido: cuatro casos verdes y un fallo en la segunda conexión del mismo proceso |
| `EVD-00004` en `…/rfc_run_000001/` | El informe de doce apartados y su matriz existen con la baseline que declaran, y el análisis no tocó código |
| `EVD-00005` en `…/rfc_run_000002/test_run_000004/` | La fase 1 medida: 10/10, suites sin perder verdes, causalidad 3/3 y repetibilidad global no cumplida |
| `EVD-00006` en `…/rfc_run_000003/test_run_000005/` | La fase 2 medida por la auditoría: los dos tests de identidad verdes en los dos árboles |
| `EVD-00007` en `…/rfc_run_000004/test_run_000006/` | El paquete de 36 ficheros de la auditoría y la reproducción de T005 sobre el árbol corregido |
| `EVD-00008` en `…/rfc_run_000004/` | El informe de la auditoría entregado, con su registro clasificado y su matriz de decisiones |

## Hallazgos

| Hallazgo | Tipo | Severidad | Estado |
|---|---|---|---|
| `FND-00001` en `…/rfc_run_000001/test_run_000001/` | `defect` | `critical` | `open` |
| `FND-00002` en `…/rfc_run_000001/test_run_000002/` | `defect` | `high` | `resolved` |
| `FND-00003` en `…/rfc_run_000001/test_run_000002/` | `defect` | `critical` | `resolved` |
| `FND-00004` en `…/rfc_run_000001/test_run_000003/` | `defect` | `critical` | `resolved` |
| `FND-00005` en `…/rfc_run_000001/` | `inconsistency` | `low` | `open` |
| `FND-00006` en `…/rfc_run_000001/` | `gap` | `low` | `open` |
| `FND-00007` en `…/rfc_run_000001/` | `inconsistency` | `low` | `open` |

`FND-00001` es el único `critical` que sigue `open`, y es el que bloquea el cierre de `TASK-00001`
conforme a `specs/FINDING.md`. Los otros tres en `open` son de severidad `low` y no bloquean nada,
pero ninguno tiene acción derivada que los cierre: su campo `actions:` está vacío.

## Limitaciones y cuestiones pendientes

- **Ningún paso registra su checkpoint ni sus intentos.** Los nueve llevan `checkpoint_ref: ''` y
  `attempts: []`. El corpus real no conserva registros de intento, así que el estado de cada paso es
  el observable, pero su punto de control no es reconstruible desde los artefactos de HACTORS.
- **Las cuatro condiciones que impiden el cierre siguen abiertas**, escritas en `execution.blockers`
  de `tasks/TASK-00001.md`. Este resumen las declara; no resuelve ninguna.
- **Las limitaciones del análisis y las de cada fase no se repiten aquí.** Están en el resumen de
  `RFC-A00001` —ocho— y en los de sus tres derivadas.
- **`PLAN-00001` está en `proposed` y sus pasos 1 a 3 se ejecutaron.** La tensión está declarada en el
  propio plan: su aprobación es de [actor: human] y no quedó registro de ella en el corpus real.
- **Las tres RFC derivadas están en `draft` aunque su trabajo se ejecutó e integró.** `draft →
  approved` es una transición de [actor: human] que no consta; cada resumen declara esa distancia
  entre el estado documental y el estado de ejecución.
- **La brecha de conservación de `rfc_t`.** El contador declara siete RFC-T y existen tres archivos. Es
  una excepción técnica que `specs/DECISIONS.md` querría en un ADR y que el propietario asentó como
  deuda fuera de este proyecto.
- **`ACT-00005` y `ACT-00009` están en `pending` con su entregable vacío**, así que la documentación
  versionada de la fase 1 y la campaña de verificación dedicada de la fase 2 no tienen ni contenido ni
  fecha.
- **La fase 3 no tiene documento real que transcribir.**
  `docs/analisis/tests/RFC-T010 — Implementation of OS Process Confinement.md` tiene cero bytes, y por
  eso `step_004` a `step_008` del plan no tienen más fuente que la auditoría.
- **`gate_003` exige un ADR que no existe.** Su criterio de aprobación pide registrar en un ADR la
  alternativa elegida entre las que la auditoría clasifique como viables; la auditoría ya clasificó y
  el ADR sigue sin crearse.
- **Este resumen no está consolidado.** `status: in-progress`, y la consolidación corresponde a
  [actor: human].

## Matriz de trazabilidad

Los objetivos del plan son los del alcance corregido; los del análisis —`G1` a `G8`— y su matriz
completa están en el resumen de `RFC-A00001`.

| Objetivo | Criterio | Evidencia | Estado |
|---|---|---|---|
| El análisis, `G1`–`G8` de `RFC-A00001` | `RFC-A00001#C1`–`#C8` | `EVD-00004` | Satisfechos los ocho |
| `O1` — cerrar T006 verificando el contrato wire en el consumidor | `RFC-A00001-F00001#C1`–`#C8` | `EVD-00005` | Siete satisfechos; `#C7` no para el conjunto completo |
| `O2` — cerrar T007 con una identidad por conexión | `RFC-A00001-F00002#C1`–`#C8` | `EVD-00006` | Seis satisfechos; `#C6` y `#C8` sin acreditar |
| `O3` — hacer decidible la corrección de T005 | `RFC-A00001-A00001#C1`–`#C8` | `EVD-00008`, `EVD-00007` | Satisfechos los ocho para la auditoría; su implementación no se inició |
| `O4` — conservar la vía mediada y los controles positivos | Los casos de control de las tres RFC derivadas | `EVD-00005`, `EVD-00006`, `EVD-00007` | Satisfecho en lo medido; las suites completas de la fase 2 no se ejecutaron |
| El cierre de la TASK | `execution.status` y sus cuatro `blockers` | Ninguna: lo que consta son las cuatro condiciones, no una evidencia que las levante | No alcanzado, `in-progress` con `target_status: done` |

## Reproducción del manifiesto

Del manifiesto de la instancia, sin reinterpretarlo:

```yaml
review:
  acceptance: pending
  accepted_by: ''
  accepted_at: ''
```

`final_state: blocked` reproduce `global_state.status` del mismo manifiesto; ninguno de los dos se
reinterpreta. Las tres dimensiones del resumen global quedan cubiertas por las secciones anteriores —
«Estado final» y «Hallazgos» por el estado, «Resultados alcanzados» y «Verificación» por los
resultados, «Matriz de trazabilidad» por la trazabilidad—, y esta sección no añade un cuarto
inventario.

## Artefactos de origen

| Artefacto | Ruta relativa al proyecto |
|---|---|
| El `workflow_run` resumido | `hactors/workflow_run_000001/manifest.yaml` |
| La TASK declarada en `identity.task_ref` | `tasks/TASK-00001.md` |
| La versión de WORKFLOW ejecutada | `workflows/WORKFLOW-00001/versions/v001/workflow.yaml` |
| El plan secuenciable | `plans/PLAN-00001 — Corrección secuenciada de los hallazgos T005, T006 y T007.md` |
| Los TEST ejecutados | `tests/TEST-00001.md`, `tests/TEST-00002.md`, `tests/TEST-00003.md` |
| La RFC inicial y sus tres derivadas | solo como relación `derives` en `manifest.yaml`; cada derivada tiene resumen autónomo |
