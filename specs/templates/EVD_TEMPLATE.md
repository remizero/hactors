<!-- schema: evidence/1.0 -->

# Plantilla de evidencia (EVD-nnnnn)

[actor: human | agent] utiliza esta plantilla al registrar una evidencia.
Lo que debe contener una evidencia y sus mínimos se definen en [EVIDENCE.md](../EVIDENCE.md).
Los campos vacíos son información por resolver, no hechos afirmados.

## Identidad

| Campo | Formato | Ejemplo |
|---|---|---|
| ID | `EVD-nnnnn` único en el proyecto | `EVD-00042` |

Un identificador retirado no se reutiliza.

## Esquema YAML

```yaml
- id: EVD-00001
  title: ""
  kind: ""
  verifies: []
  source:
    rfc: ""
    harness: ""
    execution: ""
    artifact: ""
    commit: ""
  environment:
    platform: ""
    commands: []
    outputs: []
  recorded: ""
```

## Campos

| Campo | Descripción |
|---|---|
| `id` | `EVD-nnnnn`; único en el proyecto; no se reutiliza al retirar. |
| `title` | Descripción concisa del hecho observado. |
| `kind` | Tipo de evidencia; ver tabla de tipos. |
| `verifies` | Identificadores de criterios u objetivos que respalda; referenciarlos, no redefinirlos. |
| `source.rfc` | RFC a la que queda vinculada. |
| `source.harness` | HRN y versión que la produjo; omitir si no proviene de un harness. |
| `source.execution` | task_run o workflow_run de origen, cuando exista. |
| `source.artifact` | Ruta del artefacto producido o examinado. |
| `source.commit` | Hash de la revisión examinada. |
| `environment.platform` | Plataforma donde se observó el hecho. |
| `environment.commands` | Comandos literales ejecutados, en orden. |
| `environment.outputs` | Retornos, resultados por caso y duración observados. |
| `recorded` | `YYYY-MM-DD` de registro. |

## Tipos

| `kind` | Uso |
|---|---|
| `test-output` | Salida verificable de una ejecución de prueba. |
| `artifact` | Artefacto producido y conservado. |
| `document` | Documento que registra el hecho. |
| `observation` | Hecho observado directamente, sin artefacto asociado. |

## Ubicación

La evidencia se registra directamente en el directorio del artefacto que la generó.
No existe un directorio central de evidencias.
