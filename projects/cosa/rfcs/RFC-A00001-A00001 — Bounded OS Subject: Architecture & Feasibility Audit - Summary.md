---
artifact: 'rfcs/RFC-A00001-A00001 — Bounded OS Subject: Architecture & Feasibility
  Audit.md'
title: 'Fase 3: auditoría del sujeto de sistema operativo acotado, sin implementación'
level: rfc
status: in-progress
final_state: draft
target_state: done
date: '2026-11-04'
---

Estructura y secciones: `specs/templates/SUMMARY_TEMPLATE.md`. Reglas y niveles: `specs/SUMMARY.md`.
Este resumen sintetiza y referencia; no reproduce el informe de la auditoría.

## Estado final

El estado justificable es `draft`, y la razón es solo documental: `draft → approved` es una
transición de [actor: human] que no consta registrada. La ejecución sí terminó —`rfc_run_000004` está
`completed`— y sus ocho criterios están acreditados, pero HACTORS separa el estado documental del de
ejecución y avanzar el primero no corresponde a este resumen.

`FND-00001`, `critical`, sigue `open` y esta RFC figura entre sus afectados. Conforme a
`specs/FINDING.md` el bloqueo alcanza al cierre de la TASK de origen, no al estado de esta RFC; se
declara aquí porque la auditoría reprodujo su fallo y no lo cerró.

| Criterio | Estado | Evidencia |
|---|---|---|
| C1 — el sujeto de seguridad actual identificado y el ciclo de vida real del proceso documentado | Satisfecho | `EVD-00008` |
| C2 — la relación IPC de identidad y la frontera de confinamiento actuales documentadas, y establecida la viabilidad de seccomp, de unlinkat/dirfd y de Landlock | Satisfecho | `EVD-00008` |
| C3 — las alternativas de modelo de despliegue documentadas con sus privilegios, impacto, propiedades, migración e implicaciones para T005 y T007 | Satisfecho | `EVD-00008` |
| C4 — auditados los descriptores heredados y documentadas las capacidades reales de integridad de arranque y de parada | Satisfecho | `EVD-00008` |
| C5 — preservada la separación de responsabilidades entre las tres capas e identificado dónde se solapan hoy | Satisfecho | `EVD-00008` |
| C6 — definida la evidencia necesaria para cerrar T005 y la frontera de implementación de la futura RFC | Satisfecho | `EVD-00008` |
| C7 — toda conclusión principal clasificada y D1–D11 respondidas | Satisfecho | `EVD-00008` |
| C8 — ningún mecanismo de seguridad de producción cambió como parte de la auditoría | Satisfecho | `EVD-00008` y `EVD-00007` |

## Objetivo y alcance

Determinar qué entidad posee hoy la autoridad efectiva, qué proceso del sistema operativo la ejecuta y
qué mecanismos de Linux son viables para acotarla, de modo que una RFC de implementación pueda
escribirse sobre hechos y no sobre supuestos. Los seis objetivos G1–G6 y las cinco exclusiones están
en la RFC; la primera y la que da su tipo es que la implementación queda fuera de alcance, y el
entregable es un informe.

El alcance examinado y sus diecinueve fuentes de datos están en `analysis_scope` y `data_sources`; la
metodología, en `methodology`. Nada de eso se repite aquí.

## Resultados alcanzados

| Resultado | Referencia |
|---|---|
| El sujeto actual identificado como tres entidades distintas que no se encierran entre sí: el objeto de proceso con su controlador en un hilo, los procesos que Init crea y el hijo temporal del sandbox | `root_causes` RC-4 en la RFC |
| Cuatro causas raíz con su componente responsable y su evidencia, reconstruidas contra el código de producción | `root_causes` RC-3a, RC-4, RC-5 y RC-6 en la RFC |
| Viabilidad clasificada de los tres mecanismos, con la prueba local de Landlock sobre ABI 6 y sus dos límites medidos: el descriptor preabierto conserva escritura y truncado, y un hardlink preexistente modifica un inode exterior | `EVD-00008` |
| Tres modelos de despliegue comparados; el modelo actual descartado como única frontera y el dominio nativo por servidor establecido como base obligatoria | `EVD-00008` |
| Ocho clases de descriptor auditadas ante fork y ante exec, con dos fugas medidas en ejecuciones reales | `EVD-00008` |
| D1–D11 respondidas y clasificadas todas como inferencia, ninguna como mecanismo instalado; U01–U07 como condiciones de entrada del trabajo futuro | `EVD-00008` |
| La condición de aceptación que cerraría T005, propuesta y declarada no cumplida hoy, con sus controles y sus casos de bypass derivados | `EVD-00008` |
| El paquete de evidencia conservado: treinta y seis ficheros con su manifiesto de hashes, y el hash del paquete recomputado hoy coincide con el que declara el informe | `EVD-00007` |
| T005 reproducido sobre la revisión ya corregida por las fases 1 y 2, con la admisión denegando y el mismo actor eliminando el recurso por llamada directa | `EVD-00007` |

## Decisiones

No se creó ningún `ADR-nnnnn`, y la ausencia es coherente con el resultado: las once decisiones
arquitectónicas están respondidas como recomendación clasificada de inferencia, no como decisión
adoptada. La que sí corresponde a [actor: human] es la elección operativa entre los modelos de
despliegue, que `gate_003` de `PLAN-00001` contrata como `step_004` y que no consta registrada; el
informe declara explícitamente que no autoriza provisionar cuentas ni elevar privilegios.

Los rechazos razonados de las cuatro alternativas están en `alternatives_considered` de la RFC y se
referencian allí, conforme a `specs/DECISIONS.md`.

## Verificación

La auditoría no añade tests ni modifica los existentes, así que su verificación no es una suite y no
debe leerse como baseline.

| Comprobación o fase | Objetivo | Estado | Referencia |
|---|---|---|---|
| Builds dirigidos de los objetivos examinados en ambos árboles | C8 | Satisfecha, retorno 0 en los dos | `EVD-00007` |
| Selección focalizada de doce entradas de prueba en ambos árboles | C8 | Satisfecha, 11/12 en cada árbol; el único fallo es el caso T005 | `tests/TEST-00001.md` |
| Dos ejecuciones temporales de los binarios reales de Init, kernel y servidor de ejemplo | C1, C4 | Satisfecha, con registro, demostración y apagado | `EVD-00008` |
| Sonda controlada de Landlock sobre ABI 6 | C2 | Satisfecha, con sus dos límites medidos | `EVD-00008` |
| Sonda de observación del proceso en tiempo de ejecución sobre `/proc` | C4 | Satisfecha, con la correlación de descriptor, socket y pathname | `EVD-00008` |
| Cierre de alcance del informe | C8 | Satisfecha | `EVD-00008` |

Ningún `HRN-nnnnn` participa. Los intentos fallidos de instrumentación se conservan y se describen en
el informe en lugar de omitirse, y las comprobaciones no realizadas figuran como tales.

## Evidencias

| Evidencia | Afirmación que respalda |
|---|---|
| `EVD-00008` en `hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001/rfc_run_000004/` | Que el informe existe con sus dieciséis apartados, su registro clasificado, su matriz de decisiones, su comparación de modelos, su inventario de descriptores, su condición de cierre de T005 y su cierre de alcance |
| `EVD-00007` en `…/rfc_run_000004/test_run_000006/` | Que el paquete de evidencia está conservado e íntegro, que los builds dirigidos pasaron y que la selección de doce entradas dio 11/12 en cada árbol con T005 fallando |

`EVD-00006`, que está en el `test_run` de la fase 2, también respalda afirmaciones de esta auditoría:
la medición que acredita la corrección de la fase 2 la produjo ella. Su relación con esta RFC es de
procedencia compartida, no de acreditación de sus criterios.

## Hallazgos

| Hallazgo | Tipo | Severidad | Estado |
|---|---|---|---|
| `FND-00001` en `…/rfc_run_000001/test_run_000001/` | defect | critical | open |
| `FND-00007` en `…/rfc_run_000001/` | inconsistency | low | open |

Las rutas abreviadas con `…` cuelgan de `hactors/workflow_run_000001/task_run_000001`. Ninguno se
originó en esta auditoría: los dos proceden del análisis y la declaran afectada. `FND-00001` sigue
abierto porque la propiedad de confinamiento continúa sin existir en producción, y `FND-00007` porque
el documento de entrada de la auditoría no cita como origen el mapa de fronteras ni el modelo de
seguridad donde la deuda ya estaba catalogada.

## Limitaciones y cuestiones pendientes

- **T005 sigue abierto y esta auditoría no lo cierra.** Es su consecuencia declarada: la propiedad de
  confinamiento del actor no existe en producción. Lo cierra una RFC de implementación que aún no
  existe y que debe contratar las fases 3a, 3b y 3c de `implementation_plan`.
- **Siete cuestiones sin resolver son condiciones de entrada, no resultados.** U01–U07 —perfiles de
  llamadas al sistema por binario y fase, protocolo de traspaso de sujeto, elección operativa de
  despliegue, política integral posterior, descendientes y exec posterior, resistencia a fallos y
  carreras, y reexpresión de T005 conservando su propiedad— no quedan cerradas porque el informe
  entregue una recomendación.
- **La cobertura es parcial y el informe lo declara.** No hubo traza exhaustiva de llamadas al sistema
  ni prueba completa del stack; la selección de doce entradas no es una suite completa; no se probó un
  perfil completo de COSA; no se inyectaron fallos de forma exhaustiva; y solo se verificó este host.
- **Las afirmaciones embebidas en el código pueden describir garantías mayores que las reales.** El
  propio `documentation_impact` de la RFC advierte que deben revisarse al documentar la implementación
  y no tomarse como evidencia.
- **El entregable vive fuera del control de versiones del repositorio COSA.** `docs/analisis/` está
  deliberadamente ignorado, así que un árbol de trabajo limpio allí no significa que el informe y su
  paquete no existan; lo que los acredita es el hash recomputado de `EVD-00007`.
- **`status: in-progress`.** La RFC no es terminal, así que no consolida su resumen; declararlo
  `consolidated` corresponde a [actor: human].

## Matriz de trazabilidad

| Objetivo | Criterio | Evidencia | Estado |
|---|---|---|---|
| G1 | C1, C8 | `EVD-00008`, `EVD-00007` | Satisfecho |
| G2 | C1, C2, C5, C8 | `EVD-00008`, `EVD-00007` | Satisfecho |
| G3 | C2, C8 | `EVD-00008`, `EVD-00007` | Satisfecho |
| G4 | C3, C8 | `EVD-00008`, `EVD-00007` | Satisfecho |
| G5 | C4, C8 | `EVD-00008`, `EVD-00007` | Satisfecho |
| G6 | C6, C7, C8 | `EVD-00008`, `EVD-00007` | Satisfecho |

## Historial de ejecuciones

| Instancia | Motivo | Estado inicial | Trabajo realizado | Artefactos | Evidencias y hallazgos | Resultado | Estado final |
|---|---|---|---|---|---|---|---|
| `rfc_run_000004` | Ejecutar la fase 3 en su alcance de auditoría | `pending` | Reconstrucción del modelo real contra el código de producción, dos ejecuciones temporales de binarios reales, dos sondas controladas y el informe con su registro clasificado | `ACT-00010` y `ACT-00011`, ambas completadas | `EVD-00008`; respalda `FND-00001` | Investigación arquitectónica completada, con dependencias de implementación explícitas | `completed` |
| `rfc_run_000004/test_run_000006` | Comprobar `TEST-00001` sobre la revisión auditada | `pending` | Builds dirigidos y selección focalizada de doce entradas por árbol, más la conservación del paquete de evidencia | `tests/TEST-00001.md` | `EVD-00007`; confirma `FND-00001` abierto | 11/12 en cada árbol; el único fallo es el caso T005 | `completed` |

Las rutas abreviadas cuelgan de
`hactors/workflow_run_000001/task_run_000001/rfc_run_000001/plan_run_000001`. Esta es la única de las
tres fases cuyo `rfc_run` terminó: las otras dos conservan acciones pendientes.

## Artefactos de origen

| Artefacto | Ruta relativa al proyecto |
|---|---|
| La RFC resumida | `rfcs/RFC-A00001-A00001 — Bounded OS Subject: Architecture & Feasibility Audit.md` |
| La TASK declarada en `identity.task_ref` | `tasks/TASK-00001.md`, a través de `hactors/workflow_run_000001/manifest.yaml` |
| El plan que contrata esta fase en su `step_003` | `plans/PLAN-00001 — Corrección secuenciada de los hallazgos T005, T006 y T007.md` |
| La RFC de la que deriva | `rfcs/RFC-A00001 — Security Findings Analysis: T005, T006 and T007.md`, por relación `derives` |
| Sus dos prerequisitos declarados | `rfcs/RFC-A00001-F00001 …` y `rfcs/RFC-A00001-F00002 …`, por relación `depends-on` |
| El TEST cuya propiedad reproduce | `tests/TEST-00001.md` |
| El informe y su paquete de evidencia | Fuera del proyecto, en `references` de la RFC; no son artefactos HACTORS |
