<!-- schema: harness/2.0 -->

# Plantilla de receta de harness (HRN-nnnnn)

[actor: human | agent] utiliza esta plantilla al registrar la identidad y las versiones de una receta de harness.
El catálogo y los paquetes versionados son persistentes; el harness construido es efímero.
Las reglas de origen, pertenencia, publicación y evolución se definen en [HARNESS.md](../HARNESS.md); los mínimos de la evidencia, en [EVIDENCE.md](../EVIDENCE.md). Los campos vacíos son información por resolver, no verificaciones satisfechas.

## Identidad

| Elemento | Formato | Ejemplo |
|---|---|---|
| ID | `HRN-nnnnn` único en el proyecto | `HRN-00001` |
| `version` | Entero positivo incremental dentro de la identidad | `1` |
| Directorio de versión | `v` y número con un mínimo de tres dígitos | `v001` |
| Referencia exacta | ID y directorio de versión separados por `@` | `HRN-00001@v001` |

No se reutilizan identificadores ni números de versión retirados. Una referencia fuera del proyecto debe identificar también el proyecto propietario. La referencia exacta resuelve el contenido fijado al publicarse, no la versión vigente del catálogo ni un archivo mutable.

## Catálogo: manifest.yaml

Un objeto por HARNESS en su directorio, conforme a la disposición de [HARNESS.md](../HARNESS.md). La primera entrada ilustra un borrador aún no publicado.

```yaml
id: HRN-00001
title: ""
origin: ""
affiliation: ""
current_version: null
versions:
  - version: 1
    status: draft
    content_ref: ""
    published: null
    relations: []
relations: []
created: ""
updated: ""
```

| Campo | Descripción |
|---|---|
| `id` | Identidad estable del HARNESS. |
| `title` | Descripción del catálogo; no sustituye el propósito de la receta. |
| `origin` | Referencia al artefacto que motivó su creación, normalmente un TEST. Se conserva históricamente. |
| `affiliation` | Referencia al ámbito de adscripción original: proyecto, módulo o artefacto. No declara el scope de verificación ni una ubicación física obligatoria. |
| `current_version` | Número de una versión publicada en estado `ready`, o null si ninguna se seleccionó como vigente. Es una ayuda de selección, no una referencia de ejecución. |
| `versions` | Registro de versiones, con números únicos; cada entrada corresponde al paquete `versions/vNNN/`. No contiene copias de recetas ni listas de ejecuciones. |
| `versions[].version` | Número del paquete; coincide con el número en su receta. |
| `versions[].status` | Estado de disponibilidad y verificación; ver «Estados». Se mantiene fuera del paquete. |
| `versions[].content_ref` | Referencia inmutable y recuperable al contenido completo publicado; vacía solo mientras no se publique. |
| `versions[].published` | `YYYY-MM-DD` de publicación, o null mientras el borrador no se haya congelado. |
| `versions[].relations` | Relaciones de compatibilidad cuyo origen es esta versión exacta; ver «Relaciones». |
| `relations` | Relaciones de derivación cuyo origen es esta identidad HRN; ver «Relaciones». |
| `created` / `updated` | `YYYY-MM-DD` de creación y última actualización del catálogo. |

`content_ref` debe identificar un objeto conservado y verificable: por ejemplo, un objeto árbol Git retenido que abarque todo el paquete, o un archivo conservado identificado por su hash SHA-256. La referencia incluye el mecanismo y la información necesaria para recuperarlo. No bastan una rama, un tag mutable, un enlace al archivo de trabajo ni un hash cuyo contenido ya no se conserva.

Al publicar se fijan `version`, `content_ref` y `published`; no se sustituyen ni se eliminan al retirar la versión. La identidad, el origen y la pertenencia original tampoco se reescriben por reutilización o traslado. El catálogo puede evolucionar sin modificar esas asociaciones ni los bytes publicados. Las dependencias externas se fijan según [HARNESS.md](../HARNESS.md).

### Relaciones

Cada entrada contiene `target` y `relation`; el origen es el HRN o la versión que contiene la lista, no se repite en cada vínculo.

| Lista | `relation` | Destino y significado |
|---|---|---|
| `relations` | `derived_from` | Versión exacta del HRN antecedente del que deriva esta nueva identidad. No sustituye `origin`, que identifica el artefacto que motivó crearla. |
| `versions[].relations` | `compatible_with` | TEST o versión exacta de otro HRN con la que se declara compatibilidad dentro de condiciones justificadas. No implica equivalencia de resultados ni compatibilidad transitiva o simétrica. |

Las relaciones se justifican con el alcance y las condiciones documentadas de sus destinos, y con evidencia cuando afirmen verificaciones realizadas. No se heredan automáticamente al publicar otra versión. La reutilización `uses` se registra en el grafo del proyecto conforme a [HARNESS.md](../HARNESS.md); no se duplica como `used_by` en el catálogo o el paquete.

## Paquete de versión: harness.yaml

Un objeto por versión dentro de `versions/vNNN/`, acompañado de sus scripts, datos y configuración. Este esquema describe el contenido que se congela al publicar, no un archivo que se sobrescribe al avanzar `current_version`.

```yaml
id: HRN-00001
version: 1
purpose: ""
scope: ""
out_of_scope: []
build:
  dependencies: []
  configuration: ""
  steps: []
  ready_criteria: ""
execution:
  parameters: {}
  steps: []
  evaluation_criteria: ""
reproducibility:
  requirements: []
  notes: ""
created: ""
```

| Campo | Descripción |
|---|---|
| `id` / `version` | Identifican el paquete aun fuera de su directorio; deben coincidir con el catálogo y la referencia exacta. |
| `purpose` | Qué pretende comprobar; declaración explícita del objetivo. |
| `scope` | Alcance de verificación: qué comportamientos cubre. |
| `out_of_scope` | Comportamientos deliberadamente excluidos. |
| `build.dependencies` | Prerequisitos y dependencias fijadas a contenido recuperable. |
| `build.configuration` | Configuración de construcción necesaria. |
| `build.steps` | Receta de construcción: comandos literales, en orden. |
| `build.ready_criteria` | Condición verificable que indica que el harness quedó construido; no es un resultado ya observado. |
| `execution.parameters` | Parámetros admitidos, con valores predeterminados y restricciones de uso. |
| `execution.steps` | Procedimiento de ejecución, en orden; referencias a scripts incluidos o dependencias fijadas. |
| `execution.evaluation_criteria` | Reglas para evaluar resultados; referencia los criterios del TEST sin redefinirlos. |
| `reproducibility.requirements` | Condiciones exigidas al entorno y a las revisiones examinables; no plataformas ya verificadas. |
| `reproducibility.notes` | Supuestos del entorno y limitaciones conocidas. |
| `created` | `YYYY-MM-DD` de creación del paquete. |

La revisión realmente examinada, los parámetros efectivos y el contexto de uso pertenecen a la ejecución definida en [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md#12-harness_run-ejecución-de-una-versión-de-harness), no al catálogo. Los resultados y las plataformas observadas se registran en EVD; no se añade una lista `executions` ni evidencia dentro de la versión publicada. Las búsquedas inversas utilizan `identity.harness_ref` en los runs y `source.harness` / `source.execution` en las EVD.

## Estados

El estado pertenece a cada entrada del catálogo, no a los bytes de la receta ni al resultado de un `harness_run`.

| Estado | Significado |
|---|---|
| `draft` | Versión sin verificación de reproducibilidad. Puede editarse solo antes de publicarla; un draft publicado ya es inmutable. |
| `ready` | Versión publicada cuya reproducibilidad fue verificada con evidencia, dentro de sus condiciones declaradas. |
| `retired` | Fuera de uso previsto; se conservan el paquete y sus referencias históricas. |

```text
draft → ready
draft → retired
ready → retired
```

La publicación y la verificación son distintas: se puede ejecutar un `draft` publicado para verificarlo, sin declararlo `ready` por haber creado la instancia. Si necesita correcciones después de publicarse, se crea otra versión; el draft defectuoso puede retirarse sin afirmar reproducibilidad. Retirar la versión vigente exige seleccionar otra publicada y `ready`, o dejar `current_version` en null; no modifica los runs existentes.

## Principios

1. **Receta, no instalación**: el HRN describe qué y cómo construir y ejecutar; el harness construido es efímero y no necesita conservarse.
2. **Reproducibilidad completa**: el paquete y sus dependencias conservadas permiten reconstruir el harness bajo sus condiciones declaradas.
3. **Autosuficiencia**: la inexistencia del harness construido no contradice los resultados, evidencias o hallazgos derivados de él; cada EVD conserva el contexto completo de la ejecución.
4. **Aislamiento de alcance**: sin mutación entre scopes de verificación; la regla se rige por [HARNESS.md](../HARNESS.md).
5. **Vinculación de evidencia**: cada EVD queda ligada a la versión concreta del HRN y a su ejecución, conforme a [EVIDENCE.md](../EVIDENCE.md).
