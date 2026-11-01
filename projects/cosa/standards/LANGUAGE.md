# Lenguaje y estructura de código: C++

## Alcance

Reglas del perfil C++.
[actor: human | agent] las aplica al escribir o modificar código; [actor: human | agent | ci] verifica su compilación.
Las excepciones requieren el procedimiento de [STANDARDS.md](../../../specs/STANDARDS.md#excepciones-y-cambios).

## Lenguaje y compiladores

- Utilizar ISO C++23 con `-std=c++23`.
- Soportar GCC 13 o posterior y Clang 16 o posterior, verificando también la biblioteca estándar utilizada.
- No deducir disponibilidad de una función C++23 únicamente del número de versión del compilador.
- Preferir biblioteca estándar a dependencias externas no aprobadas.
- Evitar extensiones de compilador; utilizar atributos y primitivas estándar.
- Compilar sin advertencias con `-Wall -Wextra -Werror -Wpedantic`.
- Añadir `-Wconversion -Wshadow -Wnon-virtual-dtor -Wold-style-cast`.

## Errores, tipos y atributos

- Usar `std::expected<T, E>` para errores recuperables.
- No usar excepciones en bibliotecas centrales ni rutas críticas salvo excepción aprobada.
- Marcar `noexcept` únicamente cuando la función garantice que no propaga excepciones.
- Aplicar `[[nodiscard]]` a todas las funciones que devuelvan valores o resultados de error.
- Restringir parámetros de plantilla mediante conceptos que expresen sus requisitos reales.
- Usar `std::span` para secuencias contiguas y `std::string_view` para vistas de texto de solo lectura.
- Usar `constexpr` cuando proceda; reservar `consteval` para evaluaciones necesariamente en compilación.
- Preferir `std::format` y `std::print` cuando estén disponibles y sean compatibles con las restricciones de la ruta.
- Inicializar variables al declararlas y usar inicializadores designados cuando correspondan a agregados.
- No introducir comportamiento indefinido, conversiones de estilo C ni arreglos o argumentos variádicos de estilo C.
- Usar RTTI fuera de rutas críticas solo cuando lo justifique el diseño; en rutas críticas preferir despacho explícito o estático.

Las representaciones binarias pueden requerir arreglos de tamaño fijo según [MEMORY.md](MEMORY.md); no reemplazarlos rompiendo el contrato.
La compatibilidad de vistas y conversiones con la vida y alineación del almacenamiento se rige por ese estándar.

## Cabeceras y dependencias

- Una responsabilidad por cabecera; incluir solo dependencias necesarias y evitar ciclos.
- Usar `#pragma once` al inicio.
- Agrupar inclusiones: cabecera correspondiente, mismo módulo o subsistema, terceros y biblioteca estándar.
- Mantener bloques separados; preferir declaraciones adelantadas cuando sean suficientes y válidas.
- Declarar espacios de nombres explícitos, sin depender de estado global oculto.

## Organización de clases

Ordenar primero la interfaz pública y después los detalles privados:

1. Alias de tipos y enumeraciones anidadas.
2. Construcción y destrucción.
3. Operaciones de copia y movimiento, explícitamente permitidas o eliminadas según propiedad.
4. Métodos públicos.
5. Métodos privados.
6. Datos privados.

## Parámetros

- Declarar `const` los métodos que no alteren el estado observable del objeto.
- Pasar valores pequeños y vistas por valor; objetos grandes o no triviales de consulta por `const T&`.
- Expresar transferencia de propiedad y mutación explícitamente, sin usar una referencia como sustituto ambiguo de propiedad.
- Conservar la semántica del contrato al elegir entre puntero, referencia o valor.

Los nombres se definen en NAMING.md y el formato en CODING_STYLE.md. Esta composición del perfil no provee ninguno de los dos: los dominios «Nombres» y «Formato» de la tabla de [STANDARDS.md](../../../specs/STANDARDS.md#responsabilidad-de-cada-estándar) quedan sin proveedor y su deuda consta en [TODO.md](../../../TODO.md).
