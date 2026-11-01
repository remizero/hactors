# Memoria y propiedad: perfil C++

## Alcance

[actor: human | agent] aplica estas reglas a recursos, vistas y representaciones binarias.
Las restricciones de asignación y copia de rutas críticas están en PERFORMANCE.md. Esta composición del perfil no lo provee: el dominio «Rendimiento» de la tabla de [STANDARDS.md](../../../specs/STANDARDS.md#responsabilidad-de-cada-estándar) queda sin proveedor y su deuda consta en [TODO.md](../../../TODO.md).

## Propiedad y duración

- Gestionar recursos mediante objetos propietarios RAII: memoria, descriptores, mapeos y otros recursos adquiridos.
- No usar `new` o `delete` directamente; utilizar valores, contenedores, punteros inteligentes o propietarios especializados.
- Usar `std::unique_ptr<T>` para propiedad dinámica exclusiva.
- Usar `std::shared_ptr<T>` solo cuando exista propiedad compartida real, no para ocultar una vida útil indefinida.
- Expresar observación mediante referencias, punteros no propietarios o vistas.
- Un puntero observador puede ser nulo si el contrato admite ausencia; una referencia requiere un objeto válido.
- Ninguna vista puede sobrevivir al almacenamiento observado ni a una operación que lo invalide.
- Definir si el movimiento transfiere propiedad y en qué estado queda el objeto de origen.

RAII gestiona liberación durante la vida normal de los objetos; la terminación forzada de procesos requiere la recuperación que declara el proyecto.

## Búferes

- Identificar propietario, capacidad, tamaño válido, alineación y reglas de invalidación.
- Comprobar rangos externos antes de construir vistas o interpretar datos.
- Reservar capacidad y reutilizar almacenamiento según las restricciones de PERFORMANCE.md.
- No asumir que `reserve()` elimina asignaciones: puede asignar al aumentar capacidad.

## Formatos binarios

- Definir tamaño, alineación, offsets, representación y compatibilidad en el contrato público.
- Usar tipos trivialmente copiables y de disposición estándar cuando el contrato de transmisión lo requiera.
- Declarar relleno explícito sin depender de `#pragma pack` ni de suposiciones sobre el compilador.
- Los arreglos de tamaño fijo exigidos por una representación binaria son parte del contrato.
- Comprobar con `static_assert` tamaño, alineación y propiedades necesarias.
- Verificar offsets y representación entre plataformas cuando el formato deba ser interoperable.
- No interpretar trivialidad de copia como garantía de orden de bytes o ausencia de relleno.

Ejemplo ilustrativo para un contrato de 40 bytes, no una afirmación sobre todos los formatos del proyecto:

```cpp
static_assert(sizeof(WireIdentifier) == 40);
static_assert(std::is_trivially_copyable_v<WireIdentifier>);
static_assert(std::is_standard_layout_v<WireIdentifier>);
```

## Lectura de datos externos

- No desreferenciar punteros tipados sobre almacenamiento cuya alineación y vida de objeto no estén garantizadas.
- Leer campos de búferes potencialmente desalineados mediante `std::memcpy` hacia objetos apropiados.
- Comprobar límites y representación antes de utilizar los valores leídos.
- Mantener vistas de la carga útil cuando su contrato permita evitar copias.

Las comprobaciones de memoria y los analizadores exigidos se definen en [TESTING.md](TESTING.md).
