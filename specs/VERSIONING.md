# Versionado de esquemas

## Alcance

Cada artefacto con estructura definida declara la versión de esquema que cumple. Cuando una plantilla, un estado o una relación cambian, la versión identifica el formato y activa la migración explícita de los datos existentes.

Las definiciones están en [DEFINITIONS.md](DEFINITIONS.md) y la autoridad documental en [ARTIFACTS.md](ARTIFACTS.md). Lo que se versiona es la estructura de un artefacto, no la prosa que la define: las normas de `specs/` no declaran versión de esquema, y un cambio de norma sigue el flujo de [WORKFLOW.md](WORKFLOW.md) sin consumir ninguna versión.

## Formato de versión

La versión de esquema es `<mayor>.<menor>`:

| Componente | Cambio | Compatibilidad |
|---|---|---|
| `<mayor>` | Renombrar o eliminar un campo, cambiar la semántica de un estado, reestructurar el formato. | Incompatible. Requiere migración explícita. |
| `<menor>` | Añadir un campo opcional, ampliar valores permitidos, incorporar secciones nuevas. | Compatible. Los datos existentes siguen válidos sin migración. |

Una herramienta que lee versión `X.Y` puede procesar datos `X.Z` con `Z ≤ Y`, es decir, dentro del mismo mayor. Un mayor distinto exige migración conforme a la sección correspondiente.

El valor es una cadena, no un número: `1.0` y `1.10` son distintos y se comparan componente a componente.

## Dónde se declara

| Declaración | Ubicación | Contrato |
|---|---|---|
| Comentario HTML `<!-- schema: <clave>/<mayor>.<menor> -->` en la primera línea, antes del primer encabezado. | Plantillas documentales de `specs/templates/*.md`. | La estructura del artefacto que la plantilla define. |
| Campo `schema` del documento proyectado. | `views/project.json`, conforme a [VIEWS.md](VIEWS.md#el-modelo-de-lectura). | `hactors-model/1.0`. |
| Campo `identity.workflow_version` del manifiesto. | `hactors/workflow_run_XXXXXX/manifest.yaml`, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#bloque-1-identity). | La referencia exacta `WORKFLOW-nnnnn@vNNN` de la definición que se ejecuta, no la de un esquema de artefacto. |

La plantilla documental es la fuente de verdad de su propia versión: HACTORS no mantiene un registro agregado de versiones vigentes, igual que no mantiene índices ni tablas duplicadas a mano, conforme a [PROJECTS.md](PROJECTS.md). Consultar la versión vigente de una familia es leer la primera línea de su plantilla.

Las plantillas `*.yaml` del mismo directorio aportan los valores iniciales de un esquema y no declaran una segunda versión: `evidence_template.yaml` rellena el esquema `evidence` que declara [EVD_TEMPLATE.md](templates/EVD_TEMPLATE.md), y lo mismo vale para cada par. Una plantilla YAML sin su plantilla Markdown de referencia no define un esquema.

## Versiones distintas de la de esquema

Cuatro numeraciones conviven y no se confunden entre sí ni con la versión de esquema:

| Numeración | Qué versiona | Norma |
|---|---|---|
| `HRN-nnnnn@vNNN` | Una versión publicada de una receta de verificación, inmutable al publicarse. | [HARNESS.md](HARNESS.md#almacenamiento-de-versiones) |
| `WORKFLOW-nnnnn@vNNN` | Una versión publicada de una definición de flujo, inmutable al publicarse. | [WORKFLOW.md](WORKFLOW.md#identidad-y-versiones) |
| Contadores del manifest | La identidad correlativa de artefactos e instancias, no su formato. | [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#contadores) |
| Modificador de una RFC (`AM`, `AR`, `REV`, `V2`, `PATCH`, `FX`) | La revisión documental de una RFC concreta. `V2` nombra un cambio incompatible de requisitos, no una versión de esquema. | [RFC.md](RFC.md#modificadores) |

## Política de compatibilidad

- **Mismo mayor, menor igual o superior**: lectura directa. Los campos ausentes se tratan como opcionales con su valor por defecto.
- **Mismo mayor, menor inferior**: lectura directa; el consumidor ignora campos que no reconoce.
- **Mayor distinto**: migración obligatoria antes de operar con los datos.

Un cambio de plantilla que no altere la semántica de los campos existentes —reformulación de texto, reordenamiento de secciones— no incrementa la versión. Un campo vacío es información pendiente en el artefacto, no un defecto del esquema, conforme a [VIEWS.md](VIEWS.md#artefactos).

## Migraciones

Un cambio de mayor es un cambio normativo: se propone, aprueba y cierra como una RFC conforme a [LIFECYCLE.md](LIFECYCLE.md#rfc), y la transformación de los datos existentes forma parte de su alcance o de una RFC derivada. No hay un directorio de migraciones ni un registro aparte: la RFC y su resumen acreditados por [SUMMARY.md](SUMMARY.md) son el registro de qué cambió, por qué y qué se transformó.

Toda migración especifica, como mínimo:

1. Versión origen y versión destino.
2. Cambios en el esquema: diferencia de campos, estados o relaciones.
3. Procedimiento de transformación de los datos existentes, manual o ejecutable.
4. Verificación posterior, que incluye `hactors validate` sobre cada proyecto afectado conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#16-validación-del-proyecto).

[actor: human] autoriza la migración cuando afecta datos existentes; [actor: human | agent] actualiza la declaración de la plantilla en la misma operación que transforma los datos.

## Relación con el ciclo de vida

La versión de un esquema es independiente del estado de un artefacto concreto: una RFC en `draft` y una RFC en `done` cumplen la misma versión de esquema. Un cambio de versión no altera el estado de los artefactos ni de las instancias; la migración los transforma y conserva su estado.

## Restricciones

- No operar con datos cuyo mayor difiera del que declara su plantilla sin haber aplicado la migración.
- No incrementar el mayor por un cambio que pueda expresarse como menor.
- No publicar una migración sin su verificación posterior.
- No declarar una segunda versión del mismo esquema en otro archivo: la plantilla documental es la única fuente.
- No deducir de una versión de esquema la vigencia de una receta, la identidad de un artefacto ni la revisión de una RFC.

## Lo que no existe

HACTORS no tiene un registro central de versiones vigentes, ni un directorio de migraciones, ni un comando que lea, compruebe o incremente versiones de esquema. La CLI copia los valores iniciales de las plantillas YAML y no valida la versión del esquema que produce; `hactors validate` comprueba identidad, referencias, jerarquía, contadores, hallazgos bloqueantes, el esquema de `actions:`, el grafo y el contexto activo, pero no la versión de esquema de ningún artefacto, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#16-validación-del-proyecto).
