# Ciclos de vida

## Alcance

Define estados, transiciones y condiciones de RFC, TASK, SUMMARY y flujo de integración.
WORKFLOW.md ordena las acciones; RFC_SYSTEM.md sincroniza sus representaciones.
Las transiciones que tocan más de un archivo de estado siguen el protocolo de TRANSACTIONS.md.
Los identificadores de estado se conservan en inglés; sus significados se definen aquí.

Estos estados pertenecen a los artefactos documentales y a sus flujos, no a las instancias de ejecución: cada instancia registra su propio estado observable conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md).

## Estados

| Estado | Hecho representado |
|---|---|
| `proposed` | Propuesta pendiente de admisión para su elaboración. |
| `draft` | Artefacto en redacción, todavía no autorizado para ejecución. |
| `approved` | Alcance y condiciones aprobados por la autoridad humana correspondiente. |
| `in-progress` | Trabajo autorizado iniciado. |
| `implemented` | Entregables del alcance representado producidos; no implica pruebas ni aceptación. |
| `tested` | Pruebas o comprobaciones previstas ejecutadas y resultados registrados; pueden existir fallos. |
| `under_review` | Resultado sometido a revisión y, cuando corresponda, a comprobaciones de integración. |
| `validated` | Criterios aplicables comprobados satisfactoriamente y revisión requerida completada. |
| `merged` | Cambio integrado en la rama destino; pertenece al flujo, no sustituye el cierre de RFC. |
| `done` | Alcance aceptado y cerrado con las condiciones documentales y de integración aplicables satisfechas. |
| `consolidated` | Síntesis de un resumen fijada por declaración humana; inmutable salvo reapertura. |
| `rejected` | Propuesta descartada antes de su ejecución. |
| `superseded` | Decisión sustituida explícitamente por otra RFC identificada. |
| `deprecated` | Decisión que deja de recomendarse o mantenerse, preservando su historia. |
| `cancelled` | Trabajo detenido definitivamente por disposición directa sobre él, antes de su cierre satisfactorio. |
| `aborted` | WORKFLOW detenido porque un descendiente suyo no alcanza su éxito y el alcance del flujo no se redujo. |

## RFC

```text
proposed → draft → approved → in-progress → implemented → tested
                                                           ↓
done ← merged ← validated ← under_review ←───────────────────┘
```

| Transición | Actor | Condición |
|---|---|---|
| Creación en `proposed` | `[actor: agent]` | Propuesta nueva; no autoriza ejecutarla. |
| Creación en `draft` | `[actor: human]` | Inicio de redacción. |
| `proposed` → `draft` | `[actor: human]` | Admisión como punto de partida. |
| `draft` → `approved` | `[actor: human]` | Revisión técnica de alcance, contratos y aceptación. |
| `approved` → `in-progress` | `[actor: human \| agent]` | Inicio autorizado, dependencias resueltas. |
| `in-progress` → `implemented` | `[actor: human \| agent]` | Entregables completos para todo el alcance de la RFC. |
| `implemented` → `tested` | `[actor: human \| agent]` | Ejecución y registro de las comprobaciones previstas. |
| `tested` → `under_review` | `[actor: human \| agent]` | Comprobaciones locales satisfactorias y resultado listo para revisión. |
| `under_review` → `validated` | `[actor: human]` | Revisión aprobada y criterios respaldados por evidencia. |
| `validated` → `merged` | `[actor: human]` | Cambio integrado en la rama destino cuando aplique. |
| `merged` → `done` | `[actor: human \| agent]` | Documentación sincronizada y condiciones de cierre satisfechas. |
| `validated` → `done` | `[actor: human \| agent]` | Trabajo sin integración Git, con aceptación del entregable registrada. |

Los trabajos de análisis o documentación producen sus propios entregables y comprobaciones; no simulan compilaciones ni pruebas C++.
La no aplicabilidad de una comprobación debe estar justificada en el alcance aprobado, no deducida para eludir un fallo.
Las convenciones de identidad, tipos y derivación están en [RFC.md](RFC.md).

## TASK

```text
proposed → draft → approved → in-progress → implemented → tested → done
```

La admisión y aprobación siguen las mismas responsabilidades que la RFC.
[actor: human | agent] registra las transiciones de ejecución y cierre con su evidencia.
Una TASK aprobada puede crearse directamente para ejecutar un subconjunto ya autorizado; no introduce decisiones nuevas.
El cierre exige satisfacer sus criterios, entregar su resultado al flujo acordado, que cada RFC de su alcance esté en `done` y resolver los hallazgos que lo bloquean conforme a [FINDING.md](FINDING.md).
[actor: human] autoriza el cierre de la TASK; un agente solo lo propone.
[actor: human] conserva la aprobación de cualquier cambio de alcance o decisión que la TASK descubra.
Su estructura y campos se definen en [TASK_TEMPLATE.md](templates/TASK_TEMPLATE.md).

## SUMMARY

```text
in-progress ⇄ consolidated
```

| Transición | Actor | Condición |
|---|---|---|
| Creación en `in-progress` | `[actor: human \| agent]` | El artefacto resumido existe y su síntesis empieza a registrarse. |
| Actualización en `in-progress` | `[actor: human \| agent]` | Nuevos resultados, decisiones, evidencias o hallazgos que recoger. |
| `in-progress` → `consolidated` | `[actor: human]` | El artefacto resumido alcanza su condición de finalización y ningún hallazgo `critical` o `high` de su origen queda en `open`. |
| `consolidated` → `in-progress` | `[actor: human]` | El artefacto resumido recibe una nueva ejecución; agrega registros o resúmenes nuevos y no reabre los ya consolidados. |

[actor: agent] redacta y actualiza por instrucción de [actor: human]; solo [actor: human] declara la consolidación y la reapertura.
La fase es independiente de `final_state`: este acredita el estado del artefacto resumido, no la madurez de su síntesis.
Un resumen consolidado queda inmutable; las reglas de reapertura y de la línea de acceso que se reabre están en [SUMMARY.md](SUMMARY.md#fase-y-consolidación).
Su estructura y campos se definen en [SUMMARY_TEMPLATE.md](templates/SUMMARY_TEMPLATE.md).

## WORKFLOW y acciones derivadas

```text
proposed → active → closing → closed
              ↘ cancelled
              ↘ aborted
```

`active` admite TASK nuevas; `closing` no acepta nuevas TASK pero queda pendiente de cierres humanos.
`closed` exige cada TASK de su alcance en `done` y evidencia de aceptación `[actor: human]`.
`cancelled` detiene el flujo por disposición directa sobre él; `aborted` lo detiene porque un descendiente no alcanza su éxito y `[actor: human]` no reduce el alcance del flujo. Ambas son disposición `[actor: human]`, pueden tomarse desde `active` o `closing`, son terminales y preservan el trabajo y la evidencia producidos.
Los estados de una acción (`AC-nnnnn`) se definen en PROJECT_STATE.md; una RFC alcanza `done` solo con cada acción de su alcance en `completed`.

Estos estados describen el WORKFLOW abstracto. Su instancia `workflow_run` registra el estado observable de la ejecución en `global_state.status`, con intentos y bloqueos propios, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#bloque-2-global_state); la distinción entre ambos se define en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relación-entre-workflow-y-workflow_run). Un estado de instancia no sustituye la transición documental que autoriza `[actor: human]`.

## Flujo de integración

```text
implemented → tested → under_review → validated → merged
```

[actor: human | agent] produce los entregables, ejecuta y registra las comprobaciones antes de solicitar revisión.
Las comprobaciones se registran como evidencia conforme a [EVIDENCE.md](EVIDENCE.md).
[actor: human] aprueba la revisión y realiza la integración conforme al control de versiones de la instancia.
[actor: ci] aporta resultados de las comprobaciones, pero no sustituye la aprobación.
En trabajo sin integración Git, registrar la aceptación del entregable sin inventar un estado `merged`.
Este flujo es la continuación de las transiciones de RFC, no una ruta alternativa que permita saltar `implemented` o `tested`.
El cierre de la RFC se registra después de la integración, no antes.

Las referencias a revisiones de Git son metadatos complementarios de integración, nunca el mecanismo de reconstrucción del estado: este se acredita a partir de los artefactos persistidos, sus estados y sus relaciones, conforme a [PROJECTS.md](PROJECTS.md) y a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#reconstrucción-del-estado).

## Rechazo, sustitución y cancelación

[actor: human] puede realizar las siguientes disposiciones con justificación:

- `proposed`, `draft` o `approved` → `rejected`, para RFC o TASK no iniciadas.
- Cualquier estado no terminal de ejecución → `cancelled`, preservando el trabajo y la evidencia producidos.
- WORKFLOW `active` o `closing` → `aborted`, cuando un descendiente no alcanza su éxito y `[actor: human]` no reduce el alcance del flujo.
- RFC `approved`, `under_review` o `done` → `superseded`, identificando la nueva RFC y la relación inversa.
- RFC `done` → `deprecated`, conservando su historia y el motivo de retirada.

Una RFC sustituta no hereda la aprobación de la anterior y no entra sola en el alcance del padre: `[actor: human]` la incorpora como cambio de alcance.
Los artefactos rechazados, cancelados o sustituidos no se eliminan por defecto.
Ninguna de estas disposiciones cierra satisfactoriamente a un padre; las condiciones de cierre entre niveles están en PROJECT_STATE.md.
Las excepciones a las reglas de ciclo de vida siguen el mecanismo formal de EXCEPTIONS.md.

## Iteraciones y agregación

- [actor: human | agent] puede ajustar la implementación dentro del mismo diseño en `under_review`; debe repetir las comprobaciones afectadas antes de validar.
- Fuera de ese caso, [actor: human | agent] vuelve a `in-progress` si cambia un entregable comprobado y aún no cerrado, registrando la evidencia desactualizada.
- Una TASK parcial solo representa sus propios criterios; no propagar su estado automáticamente a la RFC.
- La RFC alcanza cada hito cuando lo cumple todo su alcance, aunque sus TASK avancen por separado.
- Los cambios de diseño requieren disposición humana, no una reclasificación unilateral del ejecutor.
- Una RFC cerrada se evoluciona conforme a [RFC.md](RFC.md), sin reescribir sus requisitos históricos.
- Las invariantes de cierre entre niveles están en PROJECT_STATE.md.
