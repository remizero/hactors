# Convenciones de RFC

## Alcance

[actor: human | agent] utiliza estas convenciones al redactar, derivar o evolucionar una RFC.
La definición del artefacto está en GLOSSARY.md, sus estados en LIFECYCLE.md
y las operaciones de registro en RFC_SYSTEM.md.

## Identidad y tipos

El nombre sigue `RFC-Xnnnnn[-Ynnnnn]...[-MODnnnnn] — nombre-descriptivo.md`.
Cada segmento de tipo añade un nivel de derivación; el modificador es opcional y va al final.
Cada número tiene cinco cifras como mínimo, con ceros iniciales; no utilizar `/` ni `\` en el nombre.
La identidad completa se conserva al mover el archivo.

| Tipo | Responsabilidad principal |
|---|---|
| `A` | Análisis, investigación o evaluación. |
| `F` | Capacidad o cambio funcional. |
| `I` | Integración de capacidades o subsistemas. |
| `T` | Pruebas y validación. |
| `D` | Documentación. |

Una RFC aborda una decisión o unidad de propósito coherente; no agrupa cambios sin relación.
Los tipos no cambian la autoridad de aprobación ni implican que todo entregable sea código.

## Derivación y numeración

- Una RFC puede existir sin origen o derivar de otra, conservando su identificador como prefijo.
- Cada RFC nueva recibe el siguiente correlativo global de su tipo, también cuando es derivada.
- El alcance físico o la RFC de origen no reinician ese contador.
- Ejemplo: si `F` tiene último valor `6`, una derivada de `RFC-A00002` será `RFC-A00002-F00007`.
- Una derivada de esa feature puede ser `RFC-A00002-F00007-T00008` (tests) o `RFC-A00002-F00007-D00003` (documentación).
- La derivación se registra como relación explícita; no implica dependencia de ejecución ni aprobación heredada.
- Un modificador usa un correlativo local de la RFC y del tipo de modificador, independiente de los contadores globales.

La instancia de ejecución `rfc_run` referencia la RFC sin modificar su identidad documental. Puede estar contenida en un `task_run` o en el `plan_run` que organiza una derivación; sus planes pueden continuar esa jerarquía recursiva. Si la RFC produce artefactos TEST, sus ejecuciones se representan como `test_run` dentro del `rfc_run`, junto a sus posibles `plan_run`. TEST es un artefacto distinto de una RFC de tipo T; su inmutabilidad se define en [TESTS.md](TESTS.md). Las reglas de contención, ruta activa y profundidad de ejecución se definen en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md), separadas de la derivación documental.

## Modificadores

| Modificador | Uso |
|---|---|
| `AM` | Enmienda formal del contenido o alcance. |
| `AR` | Adenda complementaria que no altera la definición fundamental. |
| `REV` | Revisión formal de la especificación. |
| `V2` | Versión mayor incompatible o sustancialmente distinta. |
| `PATCH` | Corrección pequeña y localizada del documento. |
| `FX` | Corrección de un defecto identificado en el objeto de la RFC. |

No son marcas de cualquier edición; utilizar uno solo cuando su significado corresponda al cambio.
Ejemplo: `RFC-A00002-F00007-REV00001 — revision-del-ciclo.md`.
No quitar un modificador ya incorporado a la identidad ni renumerar documentos históricos.
Un cambio incompatible de requisitos aprobados exige un documento sucesor, no su reescritura retroactiva.
Los metadatos de estado y relaciones pueden actualizarse preservando el contenido histórico.
Nuevos modificadores requieren definición y aprobación explícitas.

## Contenido y aceptación

Usar [templates/RFC_TEMPLATE.md](templates/RFC_TEMPLATE.md) como fuente de verdad para declarar contexto, problema, objetivos,
exclusiones, contratos, dependencias, decisiones, acciones, documentación, pruebas y aceptación.
Cada objetivo debe tener al menos un criterio verificable; identificar criterios para referenciarlos desde TASK y evidencias.
Las propuestas aún abiertas deben distinguirse de las decisiones aprobadas.

Cada tipo dispone de una plantilla especializada que extiende la general con campos y secciones propias:

| Tipo | Plantilla | Información adicional |
|---|---|---|
| `A` | [templates/RFC-A_TEMPLATE.md](templates/RFC-A_TEMPLATE.md) | Análisis, causas raíz, plan de fases. |
| `F` | [templates/RFC-F_TEMPLATE.md](templates/RFC-F_TEMPLATE.md) | Arquitectura, contratos, migración, seguimiento RFC-T/RFC-D. |
| `I` | [templates/RFC-I_TEMPLATE.md](templates/RFC-I_TEMPLATE.md) | Precondiciones, composición, adopción, pruebas de integración. |
| `T` | [templates/RFC-T_TEMPLATE.md](templates/RFC-T_TEMPLATE.md) | Propiedad bajo prueba, fixture, matriz, evidencia. |
| `D` | [templates/RFC-D_TEMPLATE.md](templates/RFC-D_TEMPLATE.md) | Capas documentales, trazabilidad, verificación. |

La plantilla general sigue siendo obligatoria; las variantes añaden campos sin sustituir los comunes.
Marcar como no aplicables y justificar los campos ajenos al tipo de trabajo.

## Guía de construcción por tipo

[actor: human | agent] sigue esta guía en la fase 1 de WORKFLOW.md («Proponer y aprobar»).
La guía conecta la intención de trabajo con la plantilla adecuada; no cambia la autoridad de aprobación ni los estados de LIFECYCLE.md.

### Paso común inicial

1. Identificar el tipo de trabajo: análisis, feature, integración, tests o documentación.
2. Resolver el alcance conforme a la tabla de «Ubicaciones de la instancia» más abajo.
3. Leer la plantilla general [templates/RFC_TEMPLATE.md](templates/RFC_TEMPLATE.md) y la variante correspondiente.
4. Consultar rfc_active.md para comprobar la ausencia del identificador y resolver relaciones.

### RFC-A — Análisis

Cuándo: investigar causas raíz, evaluar alternativas o reconstruir hechos antes de decidir.
Campos clave: `analysis_scope`, `data_sources`, `methodology`, `root_causes`, `implementation_plan.phases`.
Restricción principal: no modificar código, tests ni crear commits de implementación.
Al cerrar: redactar resumen; las fases del plan pueden derivar en RFC-F independientes.

### RFC-F — Feature

Cuándo: añadir capacidad o cambio funcional con contratos y arquitectura propios.
Campos clave: `proposed_architecture`, `abi_api_contracts`, `dependency_rules`, `follow_up_rfcs`.
Restricción principal: no modificar Init ni módulos fuera del alcance aprobado.
Al cerrar: redactar resumen; proponer RFC-T para pruebas independientes y RFC-D para documentación afectada.
Cada RFC propuesta conserva su identificador y relación `derives` con esta RFC-F.

### RFC-I — Integración

Cuándo: componer features ya disponibles en una ruta productiva de extremo a extremo.
Campos clave: `preconditions`, `composition`, `adoption`, `affected_files`, `integration_tests`.
Restricción principal: no crear módulos duplicados ni implementar mecanismos ausentes en las features.
Al cerrar: redactar resumen; la integración prepara la ruta para RFC-T de verificación.

### RFC-T — Tests

Cuándo: verificar una propiedad compuesta sobre la composición productiva.
Campos clave: `property_under_test`, `fixture`, `stimuli`, `security_matrix`, `evidence`.
Restricción principal: no implementar mecanismos de seguridad ni sustituir OS por mocks.
Al cerrar: redactar resumen; un defecto productivo encontrado se informa y se deriva a su RFC/fix.

### RFC-D — Documentación

Cuándo: actualizar o crear documentación que trace garantías hasta contratos y pruebas.
Campos clave: `documentation_layers`, `content_minimum`, `traceability`, `verification`.
Restricción principal: no modificar código, tests ni promover drafts a decisiones aprobadas.
Al cerrar: redactar resumen; la documentación no subsana una garantía que los tests no demostraron.

### Resumen post-cierre

Toda RFC-A, RFC-F, RFC-I y RFC-T genera un resumen al ser terminal, conforme a [RFC_SUMMARY.md](templates/RFC_SUMMARY.md).
El resumen enlaza a la RFC, sintetiza propósito, alcance, estado, decisiones y relaciones, sin redefinir requisitos.

## Ubicaciones de la instancia

| Alcance | Ubicación relativa al proyecto |
|---|---|
| Un módulo existente, sin cambiar contratos con otros | `<module>/[<submodule>/]rfcs/` |
| Varios módulos o contratos entre ellos | `rfcs/` en la raíz del proyecto |
| Creación de un módulo aún inexistente | `rfcs/` en la raíz del proyecto hasta definir y aprobar su ubicación |

[actor: human] resuelve alcances ambiguos y aprueba reubicaciones.
Una RFC fundacional puede trasladarse al módulo una vez creada su estructura; una decisión transversal conserva ubicación global.
Cada traslado actualiza el índice y las referencias, sin cambiar la identidad.

## Relaciones

| Relación | Dirección y significado |
|---|---|
| `derives` | Origen → derivada. |
| `depends-on` | RFC dependiente → RFC requerida. |
| `informs` | Fuente de información → RFC informada; no bloquea por sí misma. |
| `validated-by` | RFC objeto de validación → RFC que define esa validación. |
| `supersedes` | RFC sucesora → RFC sustituida. |

Registrar las relaciones en las RFC y representarlas en el registro; no inferir autoridad a partir de una relación.
La sustitución conserva `supersedes` en la sucesora y `superseded_by` en la anterior.

## Resumen y registro

Toda RFC excepto RFC-D mantiene un resumen asociado: `<nombre-sin-extension> - Summary.md`.
La documentación de RFC-D es por sí misma el resumen verificable; contrastarla con el código sustituye al resumen.
Debe enlazar a la RFC y sintetizar propósito, alcance, estado, decisiones y relaciones, sin redefinir requisitos.
[actor: human | agent] actualiza resumen y registros al cambiar su fuente, dentro de la misma operación.
La plantilla [RFC_SUMMARY.md](templates/RFC_SUMMARY.md) define la estructura del resumen.
La autoridad de documentos y representaciones se rige por [ARTIFACTS.md](ARTIFACTS.md).
