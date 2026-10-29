<!-- schema: harness/1.0 -->

# Plantilla de receta de harness (HRN-nnnnn)

[actor: human | agent] utiliza esta plantilla al registrar una receta de harness.
Un harness construido es efímero; la receta es el artefacto persistente que permite reconstruirlo en cualquier equipo o estado del desarrollo.
Las ideas de fondo están en [HARNESS.md](../HARNESS.md); los mínimos de la evidencia que produce, en [EVIDENCE.md](../EVIDENCE.md).

## Identidad

| Campo | Formato | Ejemplo |
|---|---|---|
| ID | `HRN-nnnnn` único en el proyecto | `HRN-00001` |
| `version` | Entero incremental dentro de la identidad | `1` |

Un identificador retirado no se reutiliza.
Las versiones evolucionan solo dentro del scope declarado; un cambio que amplíe, altere o sustituya el alcance exige un nuevo HRN con identidad propia, conforme a la regla de aislamiento de [HARNESS.md](../HARNESS.md).

## Esquema YAML

```yaml
- id: HRN-00001
  title: ""
  version: 1
  status: draft
  purpose: ""
  scope: ""
  out_of_scope: []
  used_by: []
  source_revision: ""
  build:
    dependencies: []
    configuration: ""
    steps: []
    ready_criteria: ""
  reproducibility:
    verified_platforms: []
    notes: ""
  executions: []
  created: ""
  updated: ""
```

## Campos

| Campo | Descripción |
|---|---|
| `id` | `HRN-nnnnn`; único en el proyecto; no se reutiliza al retirar. |
| `title` | Descripción concisa del harness. |
| `version` | Versión de la receta; evoluciona solo dentro del scope declarado. |
| `status` | Estado de la receta; ver tabla de estados. |
| `purpose` | Qué pretende comprobar; declaración explícita del objetivo. |
| `scope` | Alcance de verificación: qué comportamientos cubre. |
| `out_of_scope` | Comportamientos deliberadamente excluidos. |
| `used_by` | TESTs o verificaciones que emplean esta receta. |
| `source_revision` | Revisión del árbol (commit o tag) sobre la que se verifica. |
| `build.dependencies` | Prerequisitos y dependencias para construir el harness. |
| `build.configuration` | Configuración necesaria. |
| `build.steps` | Receta de construcción: comandos literales, en orden. |
| `build.ready_criteria` | Condición verificable que indica que el harness quedó construido. |
| `reproducibility.verified_platforms` | Plataformas donde la receta se verificó reproducible. |
| `reproducibility.notes` | Supuestos del entorno y limitaciones conocidas. |
| `executions` | Referencias a EVD producidas por esta versión. |
| `created` / `updated` | `YYYY-MM-DD` de creación y última revisión. |

## Estados

| Estado | Significado |
|---|---|
| `draft` | En redacción; no verificada como reproducible. |
| `ready` | Receta verificada como reproducible; puede construirse. |
| `retired` | Sustituida por otro HRN o fuera de uso. |

```text
draft → ready
ready → retired
```

## Principios

1. **Receta, no instalación**: el HRN describe qué y cómo construir; el harness construido es efímero y no se conserva.
2. **Reproducibilidad completa**: desde la receta debe poder reconstruirse íntegramente en cualquier equipo o estado del desarrollo.
3. **Autosuficiencia**: la inexistencia del harness construido no contradice los resultados, evidencias o hallazgos derivados de él; cada EVD conserva el contexto completo de la ejecución.
4. **Aislamiento de alcance**: sin mutación entre scopes de verificación; la regla se rige por [HARNESS.md](../HARNESS.md).
5. **Vinculación de evidencia**: cada EVD queda ligada a la versión concreta del HRN y a su ejecución, conforme a [EVIDENCE.md](../EVIDENCE.md).
