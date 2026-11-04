<!-- schema: workflow/1.0 -->

# Plantilla de WORKFLOW (WORKFLOW-nnnnn)

[actor: human | agent] utiliza esta plantilla al registrar la identidad y las versiones de una definición de flujo.
El catálogo y los paquetes versionados son persistentes; el flujo que describe se ejecuta en instancias `workflow_run`.
Las fases normativas están en [WORKFLOW.md](../WORKFLOW.md); sus estados, en [LIFECYCLE.md](../LIFECYCLE.md#workflow-y-acciones-derivadas); la jerarquía y sus invariantes de cierre, en [PROJECT_STATE.md](../PROJECT_STATE.md).

## Identidad

| Elemento | Formato | Ejemplo |
|---|---|---|
| ID | `WORKFLOW-nnnnn` único en el proyecto | `WORKFLOW-00001` |
| `version` | Entero positivo incremental dentro de la identidad | `1` |
| Directorio de versión | `v` y número con un mínimo de tres dígitos | `v001` |
| Referencia exacta | ID y directorio de versión separados por `@` | `WORKFLOW-00001@v001` |

No se reutilizan identificadores ni números de versión retirados. Una referencia fuera del proyecto debe identificar también el proyecto propietario. La referencia exacta resuelve la definición fijada al publicarse, no la versión vigente del catálogo. Una definición nueva toma el número siguiente del contador `workflow_run`, que comparte con sus workflow_run y no consume al redactarla, conforme a [WORKFLOW.md](../WORKFLOW.md#identidad-y-versiones).

## Catálogo: manifest.yaml

Un objeto por WORKFLOW en su directorio, conforme a la disposición de [WORKFLOW.md](../WORKFLOW.md#identidad-y-versiones).

```yaml
id: WORKFLOW-nnnnn
title: ""
status: proposed
current_version: null
versions:
  - version: 1
    content_ref: ""
    published: null
created: ""
updated: ""
```

| Campo | Descripción |
|---|---|
| `id` | Identidad estable del WORKFLOW. |
| `title` | Descripción del catálogo; no sustituye el `purpose` de la versión. |
| `status` | Estado del WORKFLOW conforme a [LIFECYCLE.md](../LIFECYCLE.md#workflow-y-acciones-derivadas); es el contenedor de su disposición `closed`. |
| `current_version` | Número de la versión que deben seguir los `workflow_run` nuevos, o null si ninguna se seleccionó como vigente. Es una ayuda de selección, no una referencia de ejecución. |
| `versions` | Registro de versiones, con números únicos; cada entrada corresponde al paquete `versions/vNNN/`. No contiene copias de definiciones ni listas de ejecuciones. |
| `versions[].version` | Número del paquete; coincide con el número en su definición. |
| `versions[].content_ref` | Referencia inmutable y recuperable al contenido completo publicado; vacía solo mientras no se publique. |
| `versions[].published` | `YYYY-MM-DD` de publicación, o null mientras el borrador no se haya congelado. |
| `created` / `updated` | `YYYY-MM-DD` de creación y última actualización del catálogo. |

`content_ref` debe identificar un objeto conservado y verificable, con el mismo requisito que en [HRN_TEMPLATE.md](HRN_TEMPLATE.md#catálogo-manifestyaml).

El catálogo no declara campo `relations:` ni lista de TASK: el alcance de un WORKFLOW se recupera de los `workflow_run` que referencian sus versiones y de su `identity.task_ref`, igual que la reutilización de un HARNESS se recupera de sus runs. Una lista mantenida a mano sería una segunda fuente capaz de desmentir a la primera.

Al publicar se fijan `version`, `content_ref` y `published`; no se sustituyen ni se eliminan al retirar la versión. El catálogo puede evolucionar sin modificar los bytes publicados.

## Paquete de versión: workflow.yaml

Un objeto por versión dentro de `versions/vNNN/`. Este esquema describe el contenido que se congela al publicar, no un archivo que se sobrescribe al avanzar `current_version`.

```yaml
id: WORKFLOW-nnnnn
version: 1
purpose: ""
scope: ""
out_of_scope: []
steps: []
created: ""
```

| Campo | Descripción |
|---|---|
| `id` / `version` | Identifican el paquete aun fuera de su directorio; deben coincidir con el catálogo y la referencia exacta. |
| `purpose` | Qué trabajo ordena esta definición; declaración explícita del objetivo. |
| `scope` | Alcance del flujo: qué tipos de trabajo cubre. |
| `out_of_scope` | Fases de [WORKFLOW.md](../WORKFLOW.md) deliberadamente no cubiertas, con la razón de cada una. |
| `steps` | Pasos ordenados que realizan las fases; cada uno con los campos siguientes. |
| `created` | `YYYY-MM-DD` de creación del paquete. |

Cada entrada de `steps` contiene:

| Campo | Descripción |
|---|---|
| `id` | Identificador `step_XXX`, único dentro de la versión y estable entre intentos. |
| `phase` | Número de la fase de [WORKFLOW.md](../WORKFLOW.md) que el paso realiza, de `0` a `8`. |
| `title` | Qué se hace en el paso. |
| `actor` | Etiqueta de actor conforme a [DEFINITIONS.md](../DEFINITIONS.md); no concede autoridad por sí misma. |
| `exit_criteria` | Condición verificable que permite dar el paso por realizado; no es un resultado ya observado. |

El estado observado de cada paso, sus intentos y sus checkpoints viven en `global_state` del manifiesto de la ejecución, conforme a [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md#bloque-2-global_state); la definición no los registra ni los anticipa.

## Correspondencia con las fases

- Cada fase que la versión cubra produce al menos un paso; una fase sin paso es una fase excluida y consta en `out_of_scope`.
- Un paso realiza una sola fase: la correspondencia es de paso a fase, no de fase a fase.
- El orden de `steps` es el orden de ejecución previsto y respeta el de las fases; una fase puede repetirse en pasos no consecutivos cuando el flujo lo exija.
- `global_state.current_step` y las claves de `global_state.steps` de un `workflow_run` usan los `step_XXX` de la versión que declara su `identity.workflow_version`; un identificador ajeno a esa versión no describe la ejecución.

## Estados

El estado pertenece al catálogo y describe el WORKFLOW, no los bytes de una versión ni el resultado de un `workflow_run`. Sus valores y transiciones están en [LIFECYCLE.md](../LIFECYCLE.md#workflow-y-acciones-derivadas); cerrar o abortar es disposición de [actor: human] conforme a [PROJECT_STATE.md](../PROJECT_STATE.md#propiedad-del-estado).

Una versión no tiene estado propio: o está publicada —con `content_ref` y `published` fijados— o es un borrador que aún puede editarse. Un borrador publicado ya es inmutable; si necesita correcciones, se publica otra versión.

## Principios

1. **Definición, no ejecución**: el WORKFLOW dice cómo debería ser el proceso; lo observado vive en sus `workflow_run`, conforme a [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md#relación-entre-workflow-y-workflow_run).
2. **Versiones congeladas**: un `workflow_run` referencia una versión exacta y sigue describiendo esa ejecución aunque el catálogo avance.
3. **Sin índices derivados**: ni el catálogo ni el paquete duplican el alcance, las TASK ni las ejecuciones que ya registran otros artefactos.
4. **Autoridad remitida**: la plantilla no redefine fases, estados ni etiquetas de actor; remite a la norma que los fija.
