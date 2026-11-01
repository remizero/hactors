# Convenciones técnicas de pruebas

## Alcance

[actor: human | agent] aplica estas convenciones al escribir pruebas del perfil C++.
La identidad, la inmutabilidad y las ejecuciones de un TEST están en [TESTS.md](../../../specs/TESTS.md); la receta reutilizable que puede usar, en [HARNESS.md](../../../specs/HARNESS.md); la evidencia que sostiene una transición, en [EVIDENCE.md](../../../specs/EVIDENCE.md).
La estrategia de pruebas —niveles, cobertura y condiciones de aceptación— no tiene norma en HACTORS: la define el proyecto.

## Organización

- Ubicar pruebas en `<module>/[<submodule>/]tests/`.
- Nombrar los archivos unitarios `Test<ClassName>.cpp`, como `TestMessage.cpp`.
- Usar el marco de pruebas adoptado por el módulo; la admisión de un marco distinto la declara el proyecto.
- Describir en cada nombre el escenario y el resultado esperado.
- Mantener preparación, acción y comprobación claramente distinguibles.

Ejemplos de nombres con GoogleTest:

```cpp
TEST(BuilderTest, BuildRequestMessage_SetsCorrectFlagsAndPayloadSize) {}
TEST(DescriptorTest, ParseTruncatedBuffer_ReturnsNullopt) {}
```

Son ejemplos de nomenclatura, no pruebas implementadas ni evidencia de cobertura.

## Dependencias y datos

- En pruebas unitarias, sustituir E/S, tiempo, llamadas al sistema y procesos externos por dobles controlados.
- En integración, ejercitar los mecanismos reales necesarios para el contrato que se afirma verificar.
- Construir interfaces e inyección de dependencias suficientes para aislar el comportamiento, sin abstracciones especulativas.
- Fijar semillas cuando se utilice aleatoriedad y conservar las entradas que reproduzcan un fallo.
- Sincronizar por condiciones observables; no usar pausas como sustituto de sincronización.
- Limpiar recursos creados por cada prueba sin afectar recursos ajenos.

## Casos y diagnósticos

- Comprobar valores, errores y efectos observables, no solo que una llamada no termine de forma anómala.
- Incluir casos límite y entradas inválidas previstas por el contrato.
- Añadir regresiones para defectos corregidos cuando puedan reproducirse.
- Tratar una prueba inestable como defecto: corregirla; retirarla solo con justificación y sin ocultar pérdida de cobertura.
- No debilitar aserciones ni omitir pruebas para obtener una ejecución satisfactoria.

## Ejecución

[actor: human | agent | ci] utiliza los comandos y configuración de compilación del módulo.
Ejecutar por separado configuraciones de analizadores incompatibles, en particular TSan y ASan.
Registrar órdenes, versiones, resultados y limitaciones conforme a los [mínimos de una evidencia](../../../specs/EVIDENCE.md#mínimos-de-una-evidencia).
Una prueba omitida, no descubierta por el ejecutor o no ejecutada no cuenta como satisfactoria.
