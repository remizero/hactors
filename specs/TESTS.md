Inmutabilidad de los tests
Estoy de acuerdo con tu distinción, y la formularía de manera más estricta que mi propuesta anterior.
Un test definido para una RFC y un objetivo de verificación determinados no se modifica para satisfacer un objetivo distinto. Si aparece otro hallazgo, se puede reutilizar el conocimiento o la implementación del test original para crear uno nuevo, pero el test original conserva su identidad, propósito y contenido.
Hay tres operaciones distintas:
Operación	¿Permitida?	Resultado
Ejecutar un test original contra otro escenario compatible	Sí	Se genera una nueva ejecución y su correspondiente evidencia.
Referenciar el resultado original como evidencia para otro hallazgo	Sí, si es pertinente	Se establece una relación trazable sin alterar el test.
Adaptar el test para verificar un objetivo diferente	Sí, como nuevo artefacto	Se crea un nuevo test que referencia el original como antecedente.
La última distinción es fundamental: reutilizar código no es reutilizar la identidad del test.




Una vez establecido un test como artefacto identificable, su contenido y propósito de verificación no se modifican. Cualquier adaptación que cambie su objetivo o comportamiento se materializa como un nuevo artefacto, con una relación explícita con su antecedente. Las ejecuciones y sus resultados mantienen identidades independientes.

## Instancias de ejecución

La instancia `test_run` referencia el artefacto TEST mediante `identity.test_ref` y vive dentro del `rfc_run` correspondiente, inicial o derivado. Su estructura, creación y contexto activo se definen en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md); las reglas de evidencia siguen en [EVIDENCE.md](EVIDENCE.md). Crear la instancia no crea ni modifica el TEST, no lo ejecuta y no produce resultados ni evidencia automáticamente.

La reutilización de recetas versionadas sigue [HARNESS.md](HARNESS.md). Las instancias de ese uso y su vinculación al TEST solicitante se definen en [harness_run](HACTORS_SYSTEM.md#12-harness_run-ejecución-de-una-versión-de-harness): la CLI crea y selecciona estos hijos, sin ejecutar recetas ni transferir al TEST los resultados de ejecuciones anteriores.
