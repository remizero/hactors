# ¿Qué es un proyecto HACTORS?

Un proyecto HACTORS es una unidad de trabajo identificable, delimitada y evolutiva que utiliza las especificaciones, los artefactos y las reglas de SPECS para organizar la colaboración entre personas y sistemas de IA, mantener la trazabilidad de las decisiones y verificar la evolución de un sistema mediante evidencia.

Su estado debe poder reconstruirse a partir de sus artefactos persistentes, sin depender de la memoria de una persona, del contexto de una conversación con un LLM o del estado interno de una herramienta.

No hace falta que todo proyecto HACTORS sea un proyecto de software. El modelo debería servir también para investigación, diseño de sistemas, documentación técnica y otros trabajos complejos. Lo que lo convierte en un proyecto HACTORS no es el lenguaje de programación, sino la forma en que gobierna su evolución.


## Propiedades de un proyecto HACTORS.

De esta definición se desprenden seis propiedades:

1. **Identidad**: tiene un identificador estable, un nombre y una ubicación propia.
2. **Alcance**: declara qué se pretende construir, mantener o investigar y cuáles son sus límites.
3. **Autoridad normativa**: identifica las reglas que rigen el proyecto y las especificaciones aplicables.
4. **Evolución controlada**: los cambios relevantes se representan mediante RFC y decisiones trazables.
5. **Verificabilidad**: las afirmaciones de implementación, pruebas y aceptación están respaldadas por evidencia identificable.
6. **Reconstrucción del estado**: el estado actual se obtiene de fuentes de verdad persistentes y de sus relaciones, no de contadores o resúmenes mantenidos manualmente.

---

## Estructura de un proyecto HACTORS

Esta estructura define la organización física de un proyecto HACTORS del proyecto a aplicar seguimiento.

```
projects/<project_name>/
├── hactors/
├── decisions/
├── docs/
│   └── plans/
├── harnesses/
├── plans/
├── rfcs/
├── standards/
├── tasks/
├── tests/
├── trivial/
├── views/
├── workflows/
├── manifest.yaml
└── project.yaml
```

La tabla siguiente explica lo que representa la estructura anterior.

| Documento | ¿Qué es? | Descripción |
|---------------|-------------|-------------|
| hactors/      | Directorio de trabajo y evolución de las especificaciones RFCs | Donde viven los artefactos que describen la evolución y estado del proyecto. |
| decisions/    | Decisiones registradas | Cada decisión vive en su propio archivo `ADR-nnnnn — nombre-descriptivo.md`, sin registro agregado. Ver [DECISIONS.md](DECISIONS.md). |
| docs/plans/   | Planes transversales | Documentos PLAN que no produce una RFC concreta de este proyecto. Ver [templates/PLAN_TEMPLATE.md](templates/PLAN_TEMPLATE.md#ubicación). |
| harnesses/    | Recetas de verificación | Cada receta vive en `HRN-nnnnn/` con su `manifest.yaml` y sus versiones publicadas. Ver [HARNESS.md](HARNESS.md#almacenamiento-de-versiones). |
| plans/        | Planes de implementación | Documentos PLAN que produce una RFC del proyecto; cada uno declara su `origin`. Ver [templates/PLAN_TEMPLATE.md](templates/PLAN_TEMPLATE.md#ubicación). |
| rfcs/         | Especificaciones de evolución | Contenido normativo original inmutable de una RFC. Cada RFC conserva su contenido original y su identidad. El estado puede evolucionar mediante los mecanismos autorizados, sin reescribir retrospectivamente lo que se propuso. |
| standards/    | Normas específicas del proyecto | Convenciones particulares de documentación, Git y estilo de código. Solo debe redefinir reglas cuando exista una necesidad real y se respete la autoridad normativa de SPECS. |
| tasks/        | Artefactos iniciadores | Cada TASK inicia un proceso de ejecución y define su alcance y sus criterios de aceptación. Ver [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#7-task-artefacto-iniciador). |
| tests/        | Especificaciones de verificación | Un archivo por TEST, `TEST-nnnnn.md`, con su identidad y su propósito inmutable. Ver [TESTS.md](TESTS.md). |
| trivial/      | Cambios por vía rápida | Un archivo por cambio, `TRV-nnnnn — nombre-descriptivo.md`, sin libro de registro agregado. Ver [TRIVIAL.md](TRIVIAL.md#identificador-y-ubicación). |
| views/        | Vistas derivadas | Proyecciones generadas para leer el proyecto sin recorrer sus artefactos; el directorio lo crea la primera que se proyecta. Se regeneran enteras, no se editan y la CLI nunca las lee. Ver [VIEWS.md](VIEWS.md). |
| workflows/    | Definiciones de flujo | Cada definición vive en `WORKFLOW-nnnnn/` con su `manifest.yaml` y sus versiones publicadas. Ver [WORKFLOW.md](WORKFLOW.md). |
| manifest.yaml | Grafo de relaciones | Registra las relaciones entre los artefactos, sus referencias físicas, la genealogía y la temporalidad cuando corresponda. Debe permitir navegar por la evolución del proyecto sin mantener índices o tablas duplicadas manualmente. |
| project.yaml  | Identidad y configuración | Identidad el proyecto, propósito, referencias normativas y configuración necesaria para interpretarlo. No debe duplicar información derivable de otros artefactos. |

---

## Cómo crear un proyecto HACTORS.

### Manual.

1. Crear un direcctorio con el nombre del proyecto al cual se le quiere hacer seguimiento, dentro del directorio hactors/projects/.
2. Crear el archivo project.yaml dentro del directorio de proyecto recién creado hactors/projects/<project_name>, basado en la plantilla ubicada en hactors/specs/templates/project_template.yaml.
3. Crear el archivo manifest.yaml dentro del directorio de proyecto recién creado hactors/projects/<project_name>, basado en la plantilla ubicada en hactors/specs/templates/manifest_template.yaml.
4. Crear el directorio standards/, dentro del directorio hactors/projects/<project_name>, donde podrá contener los archivos DOCUMENTATION.md, GIT.md, CODING_STYLE.md propios de ese proyecto, que no son normas de HACTORS y no deben confundirse con [DOCUMENTATION.md](DOCUMENTATION.md) ni con [STANDARDS.md](STANDARDS.md).
5. Crear el directorio rfcs/, dentro del directorio hactors/projects/<project_name>, que contendrá todas las RFCs originales definidas y que serán inmutables a lo largo del proyecto al cual se hará seguimiento. El contenido original de una RFC no se reescribe; solo sus metadatos de estado y relaciones pueden actualizarse, conforme a [RFC.md](RFC.md#modificadores).
6. Crear el directorio hactors/, dentro del directorio hactors/projects/<project_name>, que contendrá el flujo de ejecución de las RFC.
7. Crear el directorio tasks/, dentro del directorio hactors/projects/<project_name>, que contendrá las TASKs que inician ese flujo.
8. Crear el directorio decisions/, dentro del directorio hactors/projects/<project_name>, que contendrá los ADR registrados por el proyecto.

`views/`, `harnesses/`, `trivial/`, `plans/`, `docs/plans/`, `tests/` y `workflows/` no se crean al iniciar el proyecto ni existe un comando que los cree por adelantado: los crea el primer artefacto que los necesite.

### Plantilla.

Copiar el directorio hactors/specs/templates/project_template/ como hactors/projects/<project_name>, con el nombre del proyecto a hacer seguimiento.

```bash
cp -r hactors/specs/templates/project_template hactors/projects/<project_name>
```

La plantilla deja vacíos `name` en project.yaml y `project` en manifest.yaml; ambos deben rellenarse con el nombre del directorio, o la CLI rechazará el proyecto.

### CLI.

ejecute

```bash
hactors create-project project_name
```