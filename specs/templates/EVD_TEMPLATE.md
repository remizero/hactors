<!-- schema: evidence/2.0 -->

# Plantilla de evidencia (EVD-nnnnn)

[actor: human | agent] utiliza esta plantilla al registrar una evidencia.
Lo que debe contener una evidencia y sus mínimos se definen en [EVIDENCE.md](../EVIDENCE.md).
Los campos vacíos son información por resolver, no hechos afirmados.

## Identidad

| Campo | Formato | Ejemplo |
|---|---|---|
| ID | `EVD-nnnnn` único en el proyecto | `EVD-00042` |

Un identificador retirado no se reutiliza. La evidencia pertenece al proyecto que la registra; su procedencia y sus relaciones no transfieren esa pertenencia ni crean copias de la evidencia.

## Esquema YAML

```yaml
- id: EVD-00001
  title: ""
  kind: ""
  relations: []
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
| `relations` | Aplicabilidad: lista de vínculos explícitos desde esta evidencia hacia criterios, objetivos o artefactos; ver «Relaciones de aplicabilidad». |
| `source` | Procedencia: contexto de la actividad, ejecución o fuente que originó la observación; no enumera los destinos que la evidencia respalda. |
| `source.rfc` | RFC en cuyo contexto se originó la observación, cuando corresponda; omitir si ya se obtiene de `source.execution`. No declara aplicabilidad. |
| `source.harness` | Referencia exacta a la versión publicada que la produjo, conforme a [HRN_TEMPLATE.md](HRN_TEMPLATE.md); nunca un alias de versión vigente. Omitir si no proviene de un harness. |
| `source.execution` | Ruta completa de la ejecución de origen, relativa al proyecto desde `hactors/`, cuando exista; conserva todos sus ancestros conforme a [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md). |
| `source.artifact` | Ruta de la fuente o del artefacto producido o examinado que originó la observación. |
| `source.commit` | Hash de la revisión examinada; no implica que la evidencia sea aplicable a otras revisiones. |
| `environment.platform` | Plataforma donde se observó el hecho. |
| `environment.commands` | Comandos literales ejecutados, en orden. |
| `environment.outputs` | Retornos, resultados por caso y duración observados. |
| `recorded` | `YYYY-MM-DD` de registro. |

## Relaciones de aplicabilidad

Cada entrada de `relations` contiene `target` y `relation`; la dirección es **esta EVD → destino**. `target` identifica el artefacto o el criterio u objetivo dentro de su artefacto, sin redefinirlo; para identificadores locales, incluir la referencia al artefacto que los define.

| `relation` | Destino y significado |
|---|---|
| `verifies` | Criterio u objetivo: aporta el resultado observado de su verificación, no necesariamente satisfactorio. |
| `supports` | RFC, TEST, HARNESS o hallazgo: aporta respaldo a una afirmación concreta de ese artefacto, no a todo su contenido. |

Una evidencia puede tener varias relaciones, incluso con artefactos distintos de su origen. Cada vínculo debe justificarse con el hecho observado y su contexto; no se deduce de la ubicación ni de `source.rfc`. Si un artefacto es a la vez origen y destino, cada vínculo expresa un papel distinto. Añadir aplicabilidad no cambia la procedencia ni los resultados registrados y no implica aprobación, cumplimiento o resolución automática.

Fragmento ilustrativo: una observación originada en una RFC puede aportar resultados para criterios de dos RFCs y respaldar un hallazgo; los destinos representan referencias por resolver en el proyecto, no verificaciones ya realizadas.

```yaml
source:
  execution: "hactors/workflow_run_000001/task_run_000001/rfc_run_000001"
relations:
  - target: "RFC-A00001#C1"
    relation: verifies
  - target: "RFC-F00002#C2"
    relation: verifies
  - target: "FND-00001"
    relation: supports
```

La aplicabilidad se declara únicamente en `relations`: no mantener una lista `verifies` paralela ni usar `source` para declarar destinos respaldados.

## Tipos

| `kind` | Uso |
|---|---|
| `test-output` | Salida verificable de una ejecución de prueba. |
| `artifact` | Artefacto producido y conservado. |
| `document` | Documento que registra el hecho. |
| `observation` | Hecho observado directamente, sin artefacto asociado. |

## Ubicación

La evidencia se registra directamente en el directorio del artefacto que la generó, en un archivo `EVD-nnnnn.yaml` por evidencia.
No existe un directorio central de evidencias.

El esquema anterior muestra la entrada como elemento de lista; el archivo escrito contiene esa misma entrada sin el guion de lista, con `id` ya asignado. Las reglas de ubicación según el origen se definen en [EVIDENCE.md](../EVIDENCE.md).

## Registro con la CLI

`hactors create-evidence` asigna el `id` y la procedencia, y acepta `--origin`, `--title`, `--kind` y `--recorded`. Sin `--origin` la procedencia es la ruta de la instancia activa. Los valores declarados se registran literalmente; los campos omitidos conservan los de [evidence_template.yaml](evidence_template.yaml), y un valor vacío explícito sustituye al de la plantilla.

El comando no rellena `relations`, `environment` ni el resto de `source`: la aplicabilidad y el contexto observado los completa quien registra, conforme a los mínimos de [EVIDENCE.md](../EVIDENCE.md). Tampoco valida `kind` contra la tabla de tipos ni el formato de `recorded`. El origen admitido y lo que el comando no hace se describen en [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md#13-registro-de-evidencia-desde-cualquier-origen).
