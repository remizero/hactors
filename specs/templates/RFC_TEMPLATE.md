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
  index: specs/INDEX_SPECS.md
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
Las acciones indican actor conforme a GLOSSARY.md; no conceden nuevas facultades de aprobación.
Los contratos incluyen errores, invariantes, propiedad y compatibilidad; indicar expresamente si hay ruptura.
Marcar como no aplicables y justificar los campos ajenos al tipo de trabajo; no inventar código para una RFC de análisis o documentación.
La ruta del índice es relativa al proyecto de esta copia y debe adaptarse al instalar SPECS en otro proyecto.
Las referencias adicionales no sustituyen la carga definida por el índice.
