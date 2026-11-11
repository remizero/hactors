<!-- schema: trivial/1.0 -->

# Plantilla de cambio trivial

[actor: human | agent] completa esta plantilla siguiendo [TRIVIAL.md](../TRIVIAL.md).
Los campos vacíos son información por resolver, no criterios satisfechos.

## Metadatos

```yaml
id: ""
title: ""
date: ""
proposed_by: ""
status: proposed
batch: false
```

`id` usa `TRV-nnnnn` y el archivo vive en el directorio que su alcance determina, conforme a [TRIVIAL.md](../TRIVIAL.md#identificador-y-ubicación).
`proposed_by` es `human` o `agent`; la declaración de trivialidad es siempre de [actor: human](../TRIVIAL.md#autoridad).
`status` usa los estados de [TRIVIAL.md](../TRIVIAL.md#estados).
`batch` indica si la propuesta agrupa múltiples cambios del mismo tipo.

## Descripción

Qué se cambia y por qué.

## Reconocimiento

Resultado del barrido: la lista completa de archivos y ubicaciones afectadas, con cada referencia verificada contra su destino.

| Archivo | Ubicación | Cambio |
|---|---|---|
| | | |

## Resultado esperado

Qué aspecto tendrán los archivos afectados tras la ejecución.

## Aprobación

[actor: human] aprueba o rechaza la propuesta. Registrar quién y cuándo.

## Ejecución

Cambios aplicados. Completar tras la ejecución si difieren de la propuesta; si difieren en alcance, el cambio es `escalated` y continúa por flujo completo.

## Registro

Este archivo es el registro: no hay un libro agregado donde añadir una entrada. Fijar `status` en `done` con su fecha al terminar.
