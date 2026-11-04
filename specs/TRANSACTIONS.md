# Protocolo transaccional de actualización

## Alcance

Define la unidad atómica de cambio sobre los artefactos y manifiestos de un proyecto. Toda operación que toque más de un archivo sigue este orden para garantizar consistencia, trazabilidad y capacidad de reconciliación.

Los identificadores y estados están en [LIFECYCLE.md](LIFECYCLE.md); la autoridad de fuentes, en [ARTIFACTS.md](ARTIFACTS.md); el grafo y los contadores, en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relaciones-del-proyecto).

HACTORS no tiene identificador de transacción ni registro de transacciones: no existe `TX-nnnnn`, el manifest no tiene contador de transacciones y ningún comando escribe el rastro de la operación. El rastro de un cambio son los archivos modificados y el estado observado de las instancias. Lo que este documento fija es el orden y los efectos que una operación debe declarar para ser consistente; la transición de estados documentales tiene su norma y su comando en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#17-transición-de-estados-documentales).

## Archivos de estado

| Archivo | Qué registra |
|---|---|
| `projects/<proyecto>/manifest.yaml` | El grafo `relations` y los contadores. |
| `projects/<proyecto>/tasks/TASK-nnnnn.md` | La TASK iniciadora y su estado de ejecución. |
| `projects/<proyecto>/rfcs/*.md` y sus resúmenes | Las RFC y su síntesis. |
| `projects/<proyecto>/decisions/ADR-nnnnn — nombre-descriptivo.md` | Las decisiones. |
| `projects/<proyecto>/plans/` y `docs/plans/` | Los PLAN. |
| `projects/<proyecto>/hactors/<instancia>/manifest.yaml` | El estado observado de cada instancia de ejecución. |
| `EVD-nnnnn.yaml` y `FND-nnnnn.yaml` junto a su origen | Evidencias y hallazgos. |
| `projects/<proyecto>/harnesses/HRN-nnnnn/` | Catálogos y paquetes de versión de receta. |
| `projects/.state.yaml` | El contexto activo, compartido por todos los proyectos de la raíz. |

`views/` no es un archivo de estado y no participa en ninguna operación: se regenera entero y la CLI nunca lo lee, conforme a [VIEWS.md](VIEWS.md).

## Orden de escritura

Toda operación sigue este orden estricto. Los pasos que no aplican se omiten sin alterar el de los restantes.

1. **Reserva de identidad**: comprobar que el identificador candidato no existe y determinar el contador que se consumirá. La CLI lo hace antes de escribir; a mano, se comprueba contra los documentos y las instancias existentes.
2. **Documento principal**: crear o modificar el artefacto —RFC, TASK, PLAN, decisión, evidencia, hallazgo, receta— o el manifiesto de la instancia.
3. **Contador**: incrementar en `manifest.yaml` el contador del tipo creado. La CLI lo incrementa y lo persiste en la reserva del paso 1, antes de escribir el documento: un fallo en el paso 2 deja el identificador consumido y el hueco documentado, que es lo que prescribe el párrafo siguiente.
4. **Relaciones**: añadir o modificar en `relations` las aristas que el documento declara.
5. **Contexto activo**: actualizar `projects/.state.yaml`, solo cuando la operación crea o selecciona una instancia.
6. **Cierre**: verificar las invariantes del tipo y dar la operación por terminada.

Si un paso falla, la operación no se considera terminada y su motivo se comunica. Los archivos ya modificados en pasos anteriores no se revierten automáticamente: la reconciliación detecta y corrige. Un identificador consumido no se reutiliza aunque el artefacto no llegue a existir; el hueco queda documentado y el contador no retrocede, así que la igualdad entre el contador y las identidades de su tipo presentes solo se restaura creando el artefacto que ese identificador reservó.

## Operaciones

| Operación | Pasos que toca | Invariante al cerrar |
|---|---|---|
| Crear una TASK. | 2, 3 | El archivo no existía; el contador `task` crece en uno. |
| Crear una RFC. | 1, 2, 4 | La identidad no existe en el proyecto; el documento declara `rfc:` y `actions:`; sus aristas están representadas. |
| Transicionar el estado documental de un artefacto o de una acción derivada. | 2 | El par actual → destino es una arista admitida por la norma de su familia y, si el destino cierra un nivel, se cumplen las invariantes de [PROJECT_STATE.md](PROJECT_STATE.md#regla-de-consistencia-entre-niveles); qué archivo se toca y qué se comprueba antes, en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#17-transición-de-estados-documentales). La arista que una disposición nombre se registra en otra operación. |
| Registrar una acción derivada. | 2, 3 | La acción no existía en esa RFC; el elemento cumple su esquema. |
| Crear una instancia de ejecución. | 2, 3, 5 | El padre es el admitido por la tabla de anidamiento; `identity.id` coincide con su componente de ruta. |
| Registrar una evidencia o un hallazgo. | 2, 3 | El origen existe; el archivo no existía en ese directorio; la procedencia reproduce el origen. |
| Crear un resumen. | 2 | El artefacto resumido existe y es de un nivel admitido; no se consume contador. |
| Crear una decisión. | 2, 3 | El archivo no existía; el contador `adr` crece en uno. |
| Registrar una arista. | 4 | Los tres campos no vacíos; el `target` resuelve; la terna no estaba registrada. |
| Publicar una versión de receta. | 2 | Se fijan `version`, `content_ref` y `published`; nada de lo fijado se reescribe al retirar la versión. |

Una operación compuesta —crear una RFC y representar sus aristas— es una sola operación si sus efectos son atómicos; si no, se divide en operaciones secuenciales, cada una con su propio orden.

## Lo que la CLI hace y no hace

Cada comando escribe su documento o manifiesto, incrementa el contador que le corresponde y, en las creaciones de instancia, actualiza el estado activo. Ninguno representa automáticamente las aristas que un documento declara: eso lo hace `hactors relate` por separado, y la completitud que falta la denuncia `hactors validate`.

Actualizar el contexto activo después de crear correctamente una instancia no implica una transacción general ante fallos de escritura, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#selección-y-creación). Ningún comando ejecuta Git ni asume que existe un repositorio Git.

## Reconciliación

La reconciliación detecta y corrige inconsistencias entre los archivos de un proyecto. Es idempotente: ejecutarla dos veces produce el mismo resultado que ejecutarla una.

### Detección

`hactors validate` es el modo de detección disponible: exige un proyecto activo, lo examina entero sobre lo ya persistido, acumula las inconsistencias y termina con error si hay alguna; no repara nada. Lo que comprueba y lo que deja fuera está en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#16-validación-del-proyecto).

De las siete verificaciones de la tabla, `hactors validate` automatiza las seis primeras. La séptima corresponde a [actor: human | agent]: sus fuentes son el resumen y el historial del documento, y no se conserva en ninguna fuente persistida el contenido anterior contra el que compararlos. La corrección, la ejecute quien la ejecute, sigue las reglas de la sección siguiente.

| Verificación | Fuentes cruzadas | Corrección canónica |
|---|---|---|
| Toda arista declarada por un documento consta en `relations`. | Documentos ↔ manifest del proyecto. | Añadir la arista que falta. |
| Todo contador iguala exactamente las identidades de su tipo presentes, y ninguna identidad existente lo excede. | Manifest ↔ documentos e instancias. | El que va por detrás se incrementa al máximo observado; el que va por delante denuncia un hueco, que se cierra creando el artefacto que ese número reservó. Una definición WORKFLOW sin ejecutar se cierra ejecutándola, no incrementando el contador. Nunca renumerar ni retroceder un contador. |
| Toda instancia tiene el padre admitido y `identity.id` igual a su componente de ruta. | Árbol de directorios ↔ manifiestos. | Corregir el manifiesto; no mover la instancia. |
| Toda referencia documental de una instancia resuelve. | `identity.*_ref` ↔ documentos y catálogos. | Corregir la referencia o registrar el artefacto ausente. |
| Ningún origen cerrado conserva un hallazgo `critical` o `high` en `open`. | `FND-nnnnn.yaml` ↔ TASK de origen. | Reconciliar en el origen que se cerró indebidamente, conforme a [FINDING.md](FINDING.md). |
| El estado activo apunta a una ruta existente y válida. | `.state.yaml` ↔ árbol de instancias. | Reseleccionar con `use-project` y `use-run`; no inferir una rama. |
| El contenido normativo de una RFC cerrada no se reescribió. | Documento ↔ su resumen y su historial. | Restaurar el contenido y registrar la revisión como documento sucesor. |

### Corrección

Aplicar la corrección canónica requiere aprobación de [actor: human] cuando elimina datos. Nunca se corrige renumerando identidades, borrando instancias ni reescribiendo lo observado: los intentos fallidos y los estados históricos se conservan.

### Ejecución

La reconciliación se ejecuta tras una operación fallida, para detectar efectos incompletos; cuando [actor: human] lo disponga, como auditoría de consistencia; y antes de dar por cerrado un nivel conforme a [PROJECT_STATE.md](PROJECT_STATE.md#regla-de-consistencia-entre-niveles).

## Restricciones

- No modificar más de un archivo de estado sin una operación que declare sus efectos.
- No asignar una identidad sin comprobar antes su ausencia.
- No considerar una operación completada sin alcanzar el paso 6.
- No revertir automáticamente los pasos anteriores a un fallo; la reconciliación corrige.
- No reconstruir el estado desde Git, desde una vista ni desde un resumen: se acredita desde los artefactos persistidos, sus estados y sus relaciones.
- Una operación no puede excepcionar este protocolo; para operar fuera de él se requiere una excepción conforme a [EXCEPTIONS.md](EXCEPTIONS.md).
