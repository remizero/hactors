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