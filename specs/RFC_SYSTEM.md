# Numeración y registro de RFC

## Alcance

Define el mecanismo administrativo de una RFC: cómo se asigna su identidad, cómo se comprueba antes de crearla, cómo se representan sus relaciones y cómo se mantiene.

Las convenciones de identidad, tipo, derivación y modificadores pertenecen a [RFC.md](RFC.md); la autoridad documental, a [ARTIFACTS.md](ARTIFACTS.md); la representación del grafo, a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relaciones-del-proyecto).

HACTORS no mantiene un índice de RFC vigentes ni un archivo de RFC terminales: el estado de una RFC se lee de la propia RFC y el de sus ejecuciones, del árbol de instancias, y la consulta agregada la responden las vistas generadas conforme a [VIEWS.md](VIEWS.md). Un proyecto sin RFC registradas no necesita inicializar ningún registro; un registro vacío no demuestra ausencia de RFC.

## Numeración

El manifest del proyecto tiene un contador por tipo de RFC: `rfc_a`, `rfc_f`, `rfc_i`, `rfc_t` y `rfc_d`, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#contadores). Los demás contadores numeran TASK, acciones derivadas, planes, TEST, HRN, decisiones, evidencias, hallazgos e instancias de ejecución; la identidad de una RFC la determina su derivación y su correlativo, el contador de su tipo.

No existe un comando que cree una RFC: el documento lo redactan [actor: human | agent] desde [RFC_TEMPLATE.md](templates/RFC_TEMPLATE.md) y su variante de tipo, conforme a [RFC.md](RFC.md#guía-de-construcción-por-tipo). La asignación sigue este orden:

1. Determinar el tipo (`A`, `F`, `I`, `T`, `D`) y la RFC de origen, si deriva de alguna.
2. Tomar el siguiente valor del contador `rfc_<tipo>` del manifest del proyecto e incrementarlo en la misma operación. El alcance físico y la RFC de origen no reinician ese contador.
3. Formar el identificador completo con toda su cadena de derivación y, si procede, su modificador.
4. Comprobar su ausencia: no existe ningún documento con esa identidad, ninguna arista del grafo la usa como extremo y ninguna instancia la referencia.
5. Crear el documento con su cabecera y su cuerpo.
6. Representar sus aristas en `relations` del manifest dentro de la misma operación.

El contador de un tipo se incorpora al manifest al declarar su primera RFC. Antes de asignar se recorren las RFC ya registradas, en cualquiera de las ubicaciones que admite [RFC.md](RFC.md#ubicación-de-una-rfc): un contador que no iguala exactamente las RFC de su tipo presentes, o que va por debajo de una identidad existente, es una inconsistencia que reporta `hactors validate`, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#contadores).

## Modificadores

El correlativo de un modificador (`AM`, `AR`, `REV`, `V2`, `PATCH`, `FX`) es local a la RFC base y al tipo de modificador, independiente de los contadores globales. Se determina desde las revisiones existentes de esa RFC base y parte de cero cuando no existe ninguna, tras comprobarlo en el proyecto.

El documento modificado se registra con su identidad completa y no consume el correlativo global del tipo. No quitar un modificador ya incorporado a la identidad ni renumerar documentos históricos.

## Concurrencia

Dos asignaciones simultáneas pueden producir el mismo identificador, porque no hay reserva ni exclusión. Mientras no exista ese mecanismo, no asignar identificadores en paralelo sobre un mismo proyecto; una asignación se comprueba y se crea antes de empezar la siguiente. `hactors validate` denuncia las identidades repetidas de `rfcs/` una vez producidas, no las evita.

## Relaciones

Una RFC declara sus relaciones en `origin`, `depends_on`, `supersedes`, `superseded_by` y en su lista `relations:`. La arista que cada campo produce está en la tabla de traducción de [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relaciones-del-proyecto); el vocabulario y sus restricciones, en [RELATIONSHIPS.md](RELATIONSHIPS.md).

La representación en `relations` del manifest es obligatoria y forma parte de la misma operación que crea o modifica el documento. Una lista vacía solo es válida mientras ninguna RFC del proyecto declare una relación representable.

`hactors relate` añade una arista y comprueba que su `target` resuelva en el proyecto; no resuelve el `source`, no resuelve el fragmento `#<identificador>` ni valida `relation` contra el vocabulario, que siguen siendo responsabilidad de quien declara la relación.

De ninguna relación se infiere autoridad, aprobación ni dependencia de ejecución.

## Actualización

[actor: human | agent] mantiene el documento y su representación desde sus fuentes:

- Cambiar solo los campos afectados; un traslado conserva la identidad completa y actualiza sus referencias y sus aristas.
- Reflejar cambios de estado, alcance y relaciones dentro de la misma operación.
- Mantener la trazabilidad de revisiones y sustituciones sin borrar evidencia histórica.
- Preservar el contenido normativo original: lo modificable es su estado y sus metadatos de relación, conforme a [RFC.md](RFC.md#modificadores), y un cambio incompatible de requisitos aprobados exige un documento sucesor.
- Si [actor: human] autoriza retirar una RFC, revisar antes sus aristas y las referencias que la apuntan.
- Las operaciones que tocan más de un archivo siguen el protocolo de [TRANSACTIONS.md](TRANSACTIONS.md).

## Comprobaciones

`hactors validate` comprueba, sobre las RFC del proyecto activo: que cada documento de `rfcs/` declare un `rfc:` legible y sin repetir, que el campo `actions:` cumpla su esquema y que las aristas del grafo resuelvan y estén completas, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#16-validación-del-proyecto).

No comprueba, y siguen siendo responsabilidad de [actor: human | agent]:

- Que el correlativo asignado sea el siguiente del tipo, ni que la cadena de derivación corresponda a una RFC de origen existente.
- Que el contenido de una RFC ya cerrada no se haya reescrito.
- Los estados, sus transiciones y las invariantes de cierre entre niveles, que pertenecen a [LIFECYCLE.md](LIFECYCLE.md) y a [PROJECT_STATE.md](PROJECT_STATE.md).
- La existencia de las RFC que una TASK lista en `rfcs:`, ni la de sus referencias internas.
