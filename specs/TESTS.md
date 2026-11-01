# TEST: identidad, inmutabilidad y ejecuciones

## Alcance

Define el TEST como artefacto: su identidad, su ubicación, su contenido mínimo, su inmutabilidad y las relaciones que declara.
Las instancias que lo ejecutan, su contención y su contexto activo pertenecen a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#11-test_run-ejecución-de-un-test); la evidencia que producen, a [EVIDENCE.md](EVIDENCE.md); las recetas reutilizables que puede usar, a [HARNESS.md](HARNESS.md).

Un TEST especifica una propiedad bajo verificación y los criterios que deciden si se cumple. No es el código que la comprueba, que vive en el sistema documentado, ni el resultado de una ejecución, que vive en la evidencia de su instancia.

## Identidad y ubicación

| Elemento | Formato | Ejemplo |
|---|---|---|
| ID | `TEST-nnnnn` único en el proyecto | `TEST-00001` |
| Documento | `tests/TEST-nnnnn.md`, en la raíz del proyecto | `tests/TEST-00001.md` |
| Campo de identidad | `id:` en un bloque `yaml` del documento | `id: TEST-00001` |

No se reutiliza un identificador retirado. El documento lo redacta [actor: human | agent] con [templates/TEST_TEMPLATE.md](templates/TEST_TEMPLATE.md); no existe un comando que lo cree, igual que ocurre con una RFC o con un PLAN. El directorio `tests/` lo crea el primer TEST, conforme a [PROJECTS.md](PROJECTS.md).

`identity.test_ref` de un test_run declara este identificador y resuelve al documento que lo porta, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#integridad-referencial). Una referencia fuera del proyecto debe identificar también el proyecto propietario.

## Inmutabilidad

Un TEST definido para una RFC y un objetivo de verificación determinados no se modifica para satisfacer un objetivo distinto. Su contenido y su propósito no cambian una vez establecido; si aparece otro hallazgo, se reutiliza el conocimiento o la implementación del original para crear un TEST nuevo, y el original conserva su identidad, su propósito y su contenido.

Hay tres operaciones distintas:

| Operación | ¿Permitida? | Resultado |
|---|---|---|
| Ejecutar un TEST original contra otro escenario compatible | Sí | Se genera una nueva ejecución y su correspondiente evidencia. |
| Referenciar el resultado original como evidencia para otro hallazgo | Sí, si es pertinente | Se establece una relación trazable sin alterar el TEST. |
| Adaptar el TEST para verificar un objetivo diferente | Sí, como nuevo artefacto | Se crea un TEST nuevo que referencia al original como antecedente. |

Reutilizar código no es reutilizar la identidad del TEST. Las ejecuciones y sus resultados mantienen identidades independientes: adaptar un TEST produce otro documento con otra identidad, nunca una revisión del primero.

## Relaciones

Un TEST declara en su campo `relations:` el antecedente del que deriva, con `derived_from` conforme a [RELATIONSHIPS.md](RELATIONSHIPS.md#vocabulario). La relación se justifica con lo que se reutiliza del antecedente y lo que cambia respecto de él; no transfiere sus resultados ni sus criterios.

La reutilización de una versión de HARNESS se representa solo en el grafo del proyecto, con `uses` y sin lista inversa en la receta, conforme a [HARNESS.md](HARNESS.md#origen-pertenencia-y-reutilización).

## Instancias de ejecución

La instancia `test_run` referencia el artefacto TEST mediante `identity.test_ref` y vive dentro del `rfc_run` correspondiente, inicial o derivado. Su estructura, creación y contexto activo se definen en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md); las reglas de evidencia siguen en [EVIDENCE.md](EVIDENCE.md). Crear la instancia no crea ni modifica el TEST, no lo ejecuta y no produce resultados ni evidencia automáticamente.

La reutilización de recetas versionadas sigue [HARNESS.md](HARNESS.md). Las instancias de ese uso y su vinculación al TEST solicitante se definen en [harness_run](HACTORS_SYSTEM.md#12-harness_run-ejecución-de-una-versión-de-harness): la CLI crea y selecciona estos hijos, sin ejecutar recetas ni transferir al TEST los resultados de ejecuciones anteriores.
