# Vía rápida para cambios triviales

## Alcance

Define una vía alternativa al flujo completo de [WORKFLOW.md](WORKFLOW.md) para cambios de bajo impacto que no justifican crear un WORKFLOW, una TASK ni una RFC.

No sustituye ni permite evadir el flujo completo; [actor: human] decide si un cambio concreto se acoge a esta vía.

## Criterios de admisibilidad

Un cambio es admisible por vía rápida solo si cumple **todos** los siguientes:

1. Afecta exclusivamente a documentación o especificaciones: archivos `.md` y `.yaml`.
2. No modifica código de producción, pruebas ni contratos.
3. No altera comportamiento, arquitectura ni interfaces.
4. No introduce decisiones técnicas ni requisitos nuevos, y no modifica una regla normativa.
5. No modifica el estado de un artefacto ni de una instancia de ejecución, ni un contador, ni el grafo del proyecto.
6. Su alcance es localizable mediante reconocimiento previo sin ambigüedad.

Ejemplos admisibles: corrección de enlaces rotos, erratas tipográficas, actualización de rutas tras un traslado de archivos, corrección de identificadores obsoletos en la prosa, ajustes de formato.

Ejemplos no admisibles: modificar una especificación normativa para cambiar una regla; añadir una sección nueva a un documento de arquitectura; corregir un contrato en código; alterar el resultado de una prueba; transicionar un estado; añadir o retirar una arista de `relations`; consumir un contador del manifest.

## Autoridad

[actor: human] declara que un cambio se acoge a la vía rápida; [actor: agent] nunca toma esa decisión por sí solo. Si [actor: agent] considera que un cambio podría ser trivial, lo propone a [actor: human] sin ejecutarlo.

## Proceso

### 1. Declaración

[actor: human] indica el cambio deseado y declara su trivialidad.

### 2. Reconocimiento

[actor: human | agent] identifica todos los puntos afectados antes de ejecutar ningún cambio. El reconocimiento puede ser mecánico —buscar y reemplazar un literal— o semántico —comprender dónde aparece un concepto y cómo se referencia—.

El resultado es la lista completa de archivos y ubicaciones afectadas, y cada referencia de esa lista se verifica contra su destino, no solo contra su sintaxis: un enlace que resuelve a un archivo puede estar afirmando algo que ese archivo no dice.

### 3. Propuesta

[actor: human | agent] registra la propuesta conforme a [TRIVIAL_TEMPLATE.md](templates/TRIVIAL_TEMPLATE.md): qué se cambia, por qué, la lista de archivos afectados y el resultado esperado.

### 4. Aprobación

[actor: human] revisa la propuesta y la aprueba o la rechaza.

### 5. Ejecución

[actor: human | agent] aplica los cambios aprobados.

### 6. Registro

[actor: human | agent] completa las secciones de ejecución y registro del propio archivo y su `status`.

## Identificador y ubicación

`TRV-nnnnn`, con cinco cifras como mínimo y ceros iniciales. El manifest del proyecto no tiene contador de cambios triviales: el siguiente correlativo se determina a partir de los archivos `TRV-*` ya existentes en el directorio que corresponda. Un identificador retirado no se reutiliza.

| Alcance del cambio | Ubicación del archivo |
|---|---|
| Un proyecto gestionado. | `projects/<proyecto>/trivial/TRV-nnnnn — nombre-descriptivo.md` |
| La copia normativa o sus guías: `specs/`, `docs/`, `README.md`, `TODO.md`. | `trivial/TRV-nnnnn — nombre-descriptivo.md`, en la raíz de la copia |

El archivo es el único registro persistente del cambio: no hay un libro de registro agregado que mantener ni que duplicar.

## Regla de corte

Si durante el reconocimiento [actor: human | agent] descubre que el cambio:

- toca código de producción, pruebas o contratos,
- requiere modificar una regla normativa,
- modifica el estado de un artefacto, de una instancia, de un contador o del grafo,
- tiene un alcance que no puede localizarse completamente,
- o introduce una decisión técnica nueva,

**se detiene** y comunica a [actor: human] que el cambio requiere flujo completo. No se ejecuta ningún cambio parcial bajo vía rápida en ese caso.

## Batching

Cuando el reconocimiento revela múltiples cambios del mismo tipo —actualizar una ruta en quince archivos—, una sola propuesta los agrupa y su tabla de reconocimiento lista todos los afectados. No se crea un `TRV-nnnnn` por archivo.

## Relación con el flujo completo

Esta vía no produce RFC, TASK ni WORKFLOW, no crea instancias de ejecución, no consume contadores del manifest y no registra aristas. Un cambio que comienza como trivial y durante el reconocimiento revela un alcance mayor se canaliza por el flujo completo sin conservar el identificador `TRV-nnnnn`, que queda en `escalated`.

## Estados

| Estado | Significado |
|---|---|
| `proposed` | Propuesta registrada, pendiente de aprobación. |
| `approved` | Aprobada por [actor: human], pendiente de ejecución. |
| `done` | Ejecutada y registrada en su propio archivo. |
| `rejected` | Rechazada por [actor: human]. |
| `escalated` | Requiere flujo completo; el identificador no se reutiliza. |

```text
proposed → approved → done
   ↘ rejected
   ↘ escalated → (flujo completo)
```

Estos estados se declaran en el campo `status` del propio archivo y no pertenecen a [LIFECYCLE.md](LIFECYCLE.md), que rige RFC, TASK, SUMMARY y WORKFLOW.

## Invariantes

1. Toda TRV tiene aprobación explícita de [actor: human] antes de su ejecución.
2. Toda TRV ejecutada conserva su archivo con las secciones de ejecución y registro completadas.
3. Una TRV `escalated` no ejecuta cambios parciales; el trabajo continúa por flujo completo.
4. Una TRV no modifica archivos fuera de la lista declarada en su reconocimiento.
5. El reconocimiento previo es obligatorio: no se ejecuta sin la lista completa de afectados.
6. Una TRV no modifica `manifest.yaml`, `projects/.state.yaml` ni el manifiesto de ninguna instancia.
