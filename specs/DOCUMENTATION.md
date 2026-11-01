# Organización de la documentación

## Alcance

Define dónde se conserva el conocimiento y cómo actualizarlo sin duplicación normativa.

Rige dos ámbitos distintos: los documentos de esta copia —`specs/`, `docs/`, `README.md`, `TODO.md`— y la documentación del sistema que un proyecto gestiona. No define el contenido de ningún artefacto: el formato de cada uno está en su especificación o en su plantilla, y la política de lectura en [CONTEXT_LOADING.md](CONTEXT_LOADING.md).

Los comentarios de código y las convenciones particulares de documentación no son normas de HACTORS: viven en el `standards/` de cada proyecto, conforme a [CONTEXT_LOADING.md](CONTEXT_LOADING.md#documentos-de-proyecto).

Conservar la historia no autoriza a presentarla como estado vigente; el historial de lo ejecutado pertenece a [PROJECT_STATE.md](PROJECT_STATE.md#historial).

## Capas

| Capa | Ubicación | Contenido |
|---|---|---|
| Normativa | `specs/` | Metodología, reglas, plantillas y política de lectura. |
| Perfiles del proyecto | `projects/<proyecto>/standards/` | Convenciones particulares de documentación, control de versiones y estilo de código. |
| Histórica y administrativa | `projects/<proyecto>/` | RFC, TASK, decisiones, acciones, evidencias, hallazgos, instancias y vistas. |
| Global del sistema seguido | El repositorio del proyecto gestionado | Contratos entre módulos, arquitectura y relaciones del sistema. |
| Local del módulo | El repositorio del proyecto gestionado | Detalle interno, componentes, implementación y pruebas del módulo. |

Las tres primeras capas viven dentro de esta copia; su estructura está en [PROJECTS.md](PROJECTS.md#estructura-de-un-proyecto-hactors). Las dos últimas no: HACTORS no aloja ni copia la documentación del sistema que sigue.

La capa global referencia el detalle local y no lo reproduce.
No reproducir dentro de `projects/<proyecto>/` la documentación global o local del sistema seguido: lo que HACTORS conserva de ese trabajo es la RFC, sus acciones, su evidencia y su resumen, no una tercera copia del documento.
Las RFC se ubican conforme a [RFC.md](RFC.md#ubicación-de-una-rfc) y su identidad se asigna conforme a [RFC_SYSTEM.md](RFC_SYSTEM.md#numeración).

## Organización interna

[actor: human | agent] debe:

- Actualizar documentación existente en lugar de reemplazarla sin necesidad.
- Mantener un punto de entrada con enlaces cuando el contenido esté repartido entre varios archivos.
- Agrupar cada archivo por una responsabilidad; dividir solo cuando haya contenido independiente.
- Usar nombres descriptivos y referencias relativas verificables contra su destino.
- Buscar aproximadamente 100 líneas por archivo como objetivo editorial, no como criterio que permita omitir información.
- Mantener reglas, condiciones y excepciones juntas; evitar fragmentación que impida interpretar un contrato.

No se exige crear un archivo por cada materia de la tabla siguiente.

## Contenido por naturaleza

| Materia | Información que debe cubrirse cuando aplique |
|---|---|
| Visión general | Propósito, alcance, objetivos y restricciones. |
| Responsabilidades | Funciones del módulo y límites con otros componentes. |
| Componentes | Entidades principales, tipos y contratos. |
| Arquitectura interna | Composición, disposición de datos y caminos de lectura y escritura. |
| Flujo de datos | Secuencias y ciclo de procesamiento. |
| Relaciones | Propiedad, dependencias y vínculos entre entidades; entre artefactos, conforme a [RELATIONSHIPS.md](RELATIONSHIPS.md). |
| Decisiones | Justificación y enlace a la decisión canónica, conforme a [DECISIONS.md](DECISIONS.md). |
| Contratos por entidad | Vida útil, concurrencia, validación, errores, invariantes y complejidad. |
| Extensión y uso | Cómo ampliar o consumir el módulo sin romper contratos. |
| Limitaciones | Restricciones vigentes y trabajo futuro claramente identificado. |
| Terminología | Términos particulares no definidos ya en [DEFINITIONS.md](DEFINITIONS.md). |
| Ejemplos | Casos completos y comprobables de uso, con sus requisitos. |
| Pruebas | Qué propiedades se verifican y con qué evidencia, conforme a [TESTS.md](TESTS.md) y [EVIDENCE.md](EVIDENCE.md). |

Utilizar diagramas ASCII cuando faciliten comprender relaciones o secuencias.
No presentar un ejemplo hipotético como descripción de una implementación comprobada.

## Idioma

La prosa de esta copia normativa y sus ejemplos explicativos está en castellano.
Los identificadores y la sintaxis de herramientas conservan su forma técnica.
La documentación del producto y los comentarios de código mantienen el inglés, salvo decisión explícita del proyecto registrada en su `standards/`.
Esta distinción evita que traducir la normativa implique traducir código o documentación ajena a la tarea.

## Actualización y cierre

1. [actor: human | agent] identifica si el cambio afecta detalle local, contratos globales, perfiles del proyecto o la propia normativa.
2. [actor: human | agent] modifica la fuente correspondiente y actualiza todas sus referencias afectadas en el mismo cambio.
3. [actor: human | agent] mantiene evidencia y decisiones históricas sin reescribirlas como si fueran estado actual.
4. [actor: human | agent | ci] verifica enlaces, estructura, ejemplos y coherencia con los entregables.
5. [actor: human | agent] incluye la documentación afectada en el mismo cambio que su implementación.

La sincronización documental es condición de cierre de una RFC conforme a [LIFECYCLE.md](LIFECYCLE.md#rfc), no trabajo opcional para una entrega posterior; el paso que la ordena está en [WORKFLOW.md](WORKFLOW.md#5-sincronizar-documentación).

Un cambio que solo corrige documentación existente y cumple los criterios de admisibilidad puede acogerse a la vía rápida de [TRIVIAL.md](TRIVIAL.md); añadir materia normativa o modificar una regla, no.
