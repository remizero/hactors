<!-- schema: summary/1.0 -->

# Plantilla de resumen

[actor: human | agent] redacta este resumen conforme a [SUMMARY.md](../SUMMARY.md).
El resumen sintetiza y referencia; no reproduce el contenido de los artefactos que resume.
Los campos vacíos son información por resolver, no secciones omitidas.

## Cabecera

```yaml
artifact: ""
title: ""
level: ""
status: "in-progress"
final_state: ""
target_state: ""
date: ""
```

| Campo | Contenido |
|---|---|
| `artifact` | El artefacto resumido, por la ruta relativa al proyecto de su origen: la RFC con su identidad completa, o el `workflow_run_XXXXXX`. |
| `title` | Descripción breve del resultado. |
| `level` | `rfc` o `workflow_run`. |
| `status` | Fase del resumen: `in-progress` o `consolidated`, conforme a [LIFECYCLE.md](../LIFECYCLE.md#summary). |
| `final_state` | Estado final justificable. Con `level: rfc`, un identificador de [LIFECYCLE.md](../LIFECYCLE.md); con `level: workflow_run`, la reproducción de `global_state.status`. |
| `target_state` | Estado objetivo, como `target_status` en una TASK. |
| `date` | `YYYY-MM-DD`. |

## Estado final

El estado que puede justificarse y los criterios de aceptación con su estado:

| Criterio | Estado | Evidencia |
|---|---|---|
| | | |

Cada criterio conserva el identificador estable que le dio su RFC, conforme a [RFC_TEMPLATE.md](RFC_TEMPLATE.md).
Distinguir los criterios satisfechos de los pendientes.
No declarar cerrado lo que las comprobaciones no demostraron.

## Objetivo y alcance

Síntesis del objetivo original, los límites fijados y las exclusiones deliberadas.
Con `level: workflow_run`, sintetizar con sus palabras la TASK declarada en `identity.task_ref` y enlazar su archivo, sin copiarla.

## Resultados alcanzados

Cada resultado afirma qué se consiguió y remite a la fuente que lo acredita:

| Resultado | Referencia |
|---|---|
| | |

No repetir el contenido de la RFC ni el de sus artefactos.

## Decisiones

| Decisión | Qué se decidió y por qué |
|---|---|
| `ADR-nnnnn` en `decisions/` | |

Una decisión que ya está registrada en la RFC o en un ADR se referencia allí; no se copia conforme a [DECISIONS.md](../DECISIONS.md).

## Verificación

Las comprobaciones ejecutadas y, cuando la RFC produjo un plan secuenciable, sus fases resultantes:

| Comprobación o fase | Objetivo | Estado | Referencia |
|---|---|---|---|
| | | | |

Un TEST se referencia por su archivo, no por su `test_run`.
Un HARNESS se referencia por la versión concreta utilizada, `HRN-nnnnn@vNNN`, conforme a [HARNESS.md](../HARNESS.md).
Omitir las filas de plan cuando la RFC no produce un plan secuenciable.

## Evidencias

| Evidencia | Afirmación que respalda |
|---|---|
| `EVD-nnnnn` en el directorio de su origen | |

Solo las que justifican un resultado afirmado, conforme a [EVIDENCE.md](../EVIDENCE.md).

## Hallazgos

| Hallazgo | Tipo | Severidad | Estado |
|---|---|---|---|
| `FND-nnnnn` en el directorio de su origen | | | |

Un hallazgo `critical` o `high` en `open` bloquea `final_state`, conforme a [FINDING.md](../FINDING.md).

## Limitaciones y cuestiones pendientes

Limitaciones que permanecen al finalizar, riesgos conocidos con su mitigación, y cuestiones donde la evidencia o el alcance no bastaron para resolverlas.
Indicar qué falta y qué RFC o trabajo puede cerrarlo.

## Matriz de trazabilidad

| Objetivo | Criterio | Evidencia | Estado |
|---|---|---|---|
| | | | |

Complementa las referencias en línea de las secciones anteriores; no las sustituye.
Conservar los identificadores estables de objetivos y criterios.

## Historial de ejecuciones

Solo con `level: rfc`. Una entrada por cada instancia que ejecuta la RFC, sin sustituir las anteriores:

| Instancia | Motivo | Estado inicial | Trabajo realizado | Artefactos | Evidencias y hallazgos | Resultado | Estado final |
|---|---|---|---|---|---|---|---|
| `rfc_run_XXXXXX` | | | | | | | |

Cubre el `rfc_run` y todos sus descendientes, incluidos los anidados bajo un `plan_run`.

## Reproducción del manifiesto

Solo con `level: workflow_run`. Se reproduce del manifiesto de la instancia, sin reinterpretarlo:

```yaml
review:
  acceptance: ""
  accepted_by: ""
  accepted_at: ""
```

`final_state` reproduce `global_state.status` del mismo manifiesto; ninguno de los dos se reinterpreta.
Las tres dimensiones del resumen global —Estado, Resultados y Trazabilidad— se cubren con las secciones anteriores; esta no añade un cuarto inventario.

## Artefactos de origen

| Artefacto | Ruta relativa al proyecto |
|---|---|
| La RFC o el workflow_run resumido | `rfcs/` o `hactors/workflow_run_XXXXXX/manifest.yaml` |
| La TASK declarada en `identity.task_ref` | `tasks/` |
| Las RFC derivadas | solo como relación `derives` |

Cada ruta conduce al archivo contenedor del artefacto. Las RFC derivadas no incorporan sus resultados aquí: tienen resumen autónomo.

## Restricciones del resumen

- No redefinir requisitos aprobados ni alterar el contenido de la RFC.
- No declarar cerrado lo que las comprobaciones no demostraron.
- No añadir análisis, arquitectura o contratos que la fuente no contenía.
- No duplicar información que ya está en otro artefacto: referenciarla.
- Enlazar a la RFC y a sus derivadas cuando existan.
- No usar referencias a revisiones de Git ni hashes de contenido como requisito de reconstrucción.

## Creación con la CLI

`hactors create-summary` escribe la cabecera como frontmatter YAML y una remisión a esta plantilla; no copia las secciones ni redacta su contenido. Acepta `--origin`, `--title`, `--status`, `--final-state`, `--target-state` y `--date`. Sin `--origin` el destino es el workflow_run de la instancia activa. `artifact` reproduce el origen y `level` se deriva de él; los valores declarados se registran literalmente, los campos omitidos conservan los de [summary_template.yaml](summary_template.yaml) y un valor vacío explícito sustituye al de la plantilla.

El comando no rellena las secciones: la síntesis, las referencias y la matriz de trazabilidad las redacta quien resume, conforme a los mínimos de [SUMMARY.md](../SUMMARY.md). Tampoco valida `status` ni `final_state` contra [LIFECYCLE.md](../LIFECYCLE.md), que define las fases del resumen y los estados del artefacto resumido, ni el formato de `date`, y no declara la consolidación, que corresponde a [actor: human]. El origen admitido y lo que el comando no hace se describen en [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md#15-creación-del-archivo-de-resumen).
