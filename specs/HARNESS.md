# HARNESS: identidad, versiones y ejecuciones

Este documento define el modelo de HARNESS; su formato se concreta en [templates/HRN_TEMPLATE.md](templates/HRN_TEMPLATE.md). La creación y selección de `harness_run` están implementadas conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#12-harness_run-ejecución-de-una-versión-de-harness); no incluyen resolver el catálogo, verificar contenido, publicar versiones ni construir o ejecutar recetas.

Un HARNESS es una receta persistente con identidad `HRN-nnnnn`, independiente del harness construido, que es efímero, y de cada instancia de ejecución que lo utiliza.

## Origen, pertenencia y reutilización

| Concepto | Significado |
|---|---|
| Origen | Artefacto que motivó la creación del HARNESS, normalmente un TEST; no el último que lo utilizó. |
| Pertenencia | Ámbito al que quedó adscrito originalmente: proyecto, módulo o artefacto identificable. No es su alcance de verificación ni su directorio actual. |
| Reutilización | Relación explícita por la que otro TEST utiliza una versión concreta de ese HARNESS. |
| Ejecución | Uso concreto con identidad `harness_run`, vinculado al contexto que lo solicita. |
| Evidencia | Registro verificable de lo observado durante esa ejecución, con identidad y aplicabilidad propias. |

El origen y la pertenencia original se conservan aunque la receta cambie de ubicación o se utilice desde otros contextos. Ninguno impone que la receta permanezca dentro del TEST que la motivó. Trasladarla requiere conservar su identidad, sus versiones y la resolución de sus referencias; no implica crear otro HARNESS ni reubicar ejecuciones históricas.

La reutilización se declara como relación **TEST → versión exacta de HRN**, mediante `uses` en el grafo del proyecto, sin mantener una lista inversa `used_by` en la receta. La relación no crea una ejecución ni prueba compatibilidad por sí sola. Si adaptar esa relación cambia el comportamiento o propósito del TEST, se respeta la inmutabilidad de [TESTS.md](TESTS.md): no se reescribe el TEST original.

## Alcance

Cada harness debe declarar explícitamente qué pretende comprobar.

```
HRN-00001

Purpose:
  Verify supervisor retention after child termination.

Scope:
  Process lifecycle + supervisor survival.

Out of scope:
  Credential transition
  SHM cleanup
  IPC authorization
```

Un harness puede evolucionar dentro de su propósito y alcance mediante versiones, sin sustituir las anteriores. Cambiar el procedimiento o corregir su implementación no equivale necesariamente a cambiar aquello que pretende comprobar.

## HARNESS Immutability and Reproducibility

Un HARNESS publicado constituye una definición inmutable de un procedimiento de ejecución. Cualquier modificación que altere su comportamiento, condiciones o criterios de evaluación deberá producir una nueva versión inmutable o un nuevo HARNESS derivado. Toda ejecución deberá identificar inequívocamente la versión exacta utilizada.

La unidad publicada es la **versión completa**, no solo el número ni el archivo de receta: incluye scripts auxiliares, datos y configuración que determinan su comportamiento. Sus dependencias externas deben quedar fijadas a contenido identificable y recuperable, no a ramas, etiquetas mutables o descargas que puedan cambiar silenciosamente.

Cada versión publicada vincula permanentemente la identidad HRN, su número y una referencia inmutable al contenido completo conservado. La publicación congela esa asociación y todos los archivos del paquete; una ruta o un número sobre un archivo sobrescribible no bastan. Si el contenido no coincide con la referencia fijada, no se ejecuta bajo esa versión ni se le atribuyen resultados nuevos.

La conservación de la receta permite reconstruir el harness dentro de las condiciones que declara; no garantiza que cualquier equipo cumpla esas condiciones ni que toda ejecución produzca el mismo resultado.

## Almacenamiento de versiones

Disposición de referencia dentro del proyecto, separada de las ejecuciones:

```text
harnesses/
└── HRN-00001/
    ├── manifest.yaml
    └── versions/
        ├── v001/
        │   ├── harness.yaml
        │   └── check.py
        ├── v002/
        │   ├── harness.yaml
        │   └── check.py
        └── v003/
            ├── harness.yaml
            └── check.py
```

El manifiesto es el catálogo de la identidad: conserva origen, pertenencia original, versión vigente, historial de versiones y relaciones de derivación y compatibilidad. El esquema y la notación de referencias exactas se definen únicamente en [HRN_TEMPLATE.md](templates/HRN_TEMPLATE.md). El historial referencia paquetes, no copia sus recetas ni enumera sus ejecuciones.

El catálogo puede actualizar su descripción, relaciones, estado de disponibilidad o versión vigente sin modificar los paquetes publicados. Ni una corrección editorial dentro de un paquete permite sobrescribirlo: se publica otra versión o se registra la aclaración fuera de él. Los directorios ilustrados no son `harness_run`; mover el catálogo y sus paquetes preservando su contenido no cambia su identidad histórica.

La versión vigente es una ayuda de selección, nunca la referencia histórica de una ejecución. Antes de ejecutar se resuelve a una versión publicada exacta y se fija su referencia de contenido; cambiar después la vigente no retargetea ninguna ejecución. Un borrador no publicado puede editarse, pero debe congelarse antes de usarse como versión identificable en un `harness_run`; publicar no equivale a haber verificado su reproducibilidad.

## Evolución

| Cambio | Resultado |
|---|---|
| Modificar el procedimiento de ejecución | Nueva versión inmutable, si mantiene propósito y alcance. |
| Cambiar parámetros predeterminados | Nueva versión inmutable. |
| Modificar criterios de evaluación dentro del mismo propósito y alcance | Nueva versión inmutable. |
| Corregir un script auxiliar que afecta al comportamiento | Nueva versión inmutable. |
| Corregir metadatos descriptivos del catálogo o añadir relaciones justificadas | No exige nueva versión; no modifica el paquete ni reescribe origen o pertenencia original. |
| Trasladar un paquete intacto o seleccionar otra versión vigente | No exige nueva versión; se conserva la resolución histórica. |
| Cambiar parámetros efectivos dentro de lo admitido por la receta | Nueva ejecución, no nueva versión; los valores utilizados quedan registrados. |
| Cambiar el propósito fundamental o ampliar, alterar o sustituir el alcance de verificación | Nuevo HRN relacionado con su antecedente mediante `derived_from`. |

## Verification Harness Isolation Rule

Cada harness debe tener un alcance de verificación explícito. Un cambio que amplíe, altere o sustituya dicho alcance requiere un nuevo harness con identidad propia; no se acumulan propósitos incompatibles como versiones de una misma receta. El nuevo HRN conserva su propio origen y pertenencia, y referencia la versión antecedente mediante `derived_from` sin modificarla.

No harness mutation across verification scopes.

## Ejecuciones y evidencia

La contención, identidad y contexto activo de `harness_run` se definen en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#12-harness_run-ejecución-de-una-versión-de-harness). La referencia a la versión no convierte su directorio en padre de la ejecución ni vincula esta al TEST histórico de origen.

**Reutilizar la receta no significa reutilizar automáticamente la validez de sus resultados.** Por ejemplo, dos TESTs compatibles pueden usar `HRN-00001@v002`, cada uno con sus propias ejecuciones y evidencias; compartir versión no comparte identidad de ejecución ni acredita los criterios del otro TEST.

Los resultados identifican la versión exacta, la ejecución, la revisión examinada, la construcción, la configuración efectiva y el entorno observado. Las EVD se registran junto al `harness_run` que las produjo, no dentro del paquete inmutable ni en un directorio central. Su procedencia y aplicabilidad se declaran según [EVD_TEMPLATE.md](templates/EVD_TEMPLATE.md), y conservan por sí mismas el contexto exigido por [EVIDENCE.md](EVIDENCE.md).

Una evidencia anterior puede respaldar otro destino solo mediante una relación de aplicabilidad explícita y justificada por sus hechos y condiciones, sin presentarla como una nueva ejecución. Un hallazgo detectado durante el uso sigue [FINDING.md](FINDING.md): el contexto que lo reveló no implica que el HRN esté afectado.
