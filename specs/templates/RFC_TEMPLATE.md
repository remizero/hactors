<!-- schema: rfc/1.0 -->

# Plantilla general de RFC

[actor: human | agent] completa esta plantilla siguiendo [RFC.md](../RFC.md).
Los campos vacíos son información por resolver, no criterios satisfechos.
Los estados y autorizaciones proceden de [LIFECYCLE.md](../LIFECYCLE.md).

## Metadatos

Al crear el documento, colocar este bloque como bloque de código `yaml` al inicio del archivo.
El ejemplo usa `draft` para redacción humana; una propuesta de agente comienza en `proposed`.

```yaml
rfc: ""
title: ""
type: ""
scope: ""
status: draft
date: ""
proposed_by: ""
origin: null
supersedes: null
superseded_by: null
depends_on: []
affected_modules: []
relations: []
```

`date` usa `YYYY-MM-DD`; `origin` identifica la RFC de origen, cuando exista.
Cada elemento de `relations` contiene `target` y `relation`; el origen de la relación es esta RFC.
`origin`, `depends_on`, `supersedes` y `superseded_by` ya declaran sus relaciones: no duplicarlas en `relations`.
`proposed_by` registra autoría, no autorización de ejecución.

## Cuerpo

```yaml
context: ""
problem_statement: ""
goals: []
non_goals: []
required_specifications:
  index: specs/CONTEXT_LOADING.md
  additional: []
proposed_architecture: ""
abi_api_contracts: ""
new_module: null
ownership_changes: ""
dependency_rules: ""
actions: []
migration_plan: ""
benefits:
  architectural: ""
  engineering: ""
  ai: ""
risks: []
alternatives_considered: []
consequences: ""
documentation_impact: ""
testing: ""
acceptance_criteria: []
references: []
```

Los objetivos y criterios deben tener identificadores estables para enlazarlos desde TASK y evidencias.
Cada criterio declara la condición verificable, los objetivos que cubre y cómo se comprobará.
Las acciones indican actor conforme a [DEFINITIONS.md](../DEFINITIONS.md); no conceden nuevas facultades de aprobación.
Los contratos incluyen errores, invariantes, propiedad y compatibilidad; indicar expresamente si hay ruptura.
Marcar como no aplicables y justificar los campos ajenos al tipo de trabajo; no inventar código para una RFC de análisis o documentación.
La ruta del índice es relativa al proyecto de esta copia y debe adaptarse al instalar SPECS en otro proyecto.
Las referencias adicionales no sustituyen la carga definida por el índice.

## Acciones derivadas

Cada elemento de `actions:` es una acción derivada (`AC-nnnnn`); sus tipos, sus estados y su regla de evidencia se definen en [AC_TEMPLATE.md](AC_TEMPLATE.md):

```yaml
actions:
  - id: AC-00001
    type: ""
    status: pending
    actor: ""
    depends_on: []
    deliverable: ""
    evidence: []
```

| Campo | Descripción |
|---|---|
| `id` | `AC-nnnnn`, único en el proyecto; no se reutiliza al retirar la acción. |
| `type` | Uno de los tipos de [AC_TEMPLATE.md](AC_TEMPLATE.md#tipos); no se definen tipos locales. |
| `status` | Uno de los estados de [AC_TEMPLATE.md](AC_TEMPLATE.md#estados); una RFC no alcanza `done` mientras alguna acción de su alcance no esté en `completed`. |
| `actor` | Etiqueta de [DEFINITIONS.md](../DEFINITIONS.md#actores) que ejecuta la acción, sin el envoltorio `[actor: ]`: una o varias etiquetas combinadas, o `...` para prohibirla a todos. |
| `depends_on` | `AC-nnnnn` que deben completarse antes; con alguna dependencia sin resolver, la acción está `blocked`. |
| `deliverable` | Artefacto o ruta que la acción produce; vacío mientras no exista. |
| `evidence` | `EVD-nnnnn` que respaldan el resultado; `completed` exige al menos una, conforme a [AC_TEMPLATE.md](AC_TEMPLATE.md#evidencia). |

El actor de cada transición y la propiedad del estado están en [PROJECT_STATE.md](../PROJECT_STATE.md#transiciones-de-una-acción); esta plantilla fija la forma del registro, no su ciclo de vida.

`hactors create-action --rfc <ruta>` añade un elemento a este campo con el contador `action` del manifest del proyecto: lo inserta al final de la lista sin reescribir el resto del bloque, toma los valores iniciales de [action_template.yaml](action_template.yaml) y acepta `--type`, `--status`, `--actor`, `--deliverable`, `--depends-on` y `--evidence`. Exige que el archivo declare `rfc:` y un campo `actions:` en forma de bloque, y comprueba los valores declarados contra los tipos y los estados de [AC_TEMPLATE.md](AC_TEMPLATE.md) y las etiquetas de actor de [DEFINITIONS.md](../DEFINITIONS.md#actores).

El comando no produce el entregable ni la evidencia de la acción, no comprueba que exista el `AC-nnnnn` de `depends_on` ni el `EVD-nnnnn` de `evidence`, y no la hace cambiar de estado: registra el `status` declarado y el actor de cada transición sigue en [PROJECT_STATE.md](../PROJECT_STATE.md#transiciones-de-una-acción). Tampoco la representa en `relations` del manifest del proyecto, porque la correspondencia de [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md#relaciones-del-proyecto) no traduce ninguno de sus campos.
