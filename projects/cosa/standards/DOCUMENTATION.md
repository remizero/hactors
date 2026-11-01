# Documentación de código

## Alcance

[actor: human | agent] aplica estas reglas a interfaces y comentarios del perfil C++.
La organización documental está en [DOCUMENTATION.md](../../../specs/DOCUMENTATION.md#organización-interna) y los idiomas en [su sección de idioma](../../../specs/DOCUMENTATION.md#idioma); ninguna de las dos debe confundirse con este perfil, que gobierna los comentarios del código.
Los ejemplos explicativos de esta especificación se muestran en castellano.

## Reglas

- Documentar las API públicas de cabeceras mediante bloques compatibles con Doxygen.
- Explicar intención, contrato, límites e invariantes, no repetir la sintaxis del código.
- Conservar la documentación junto a la declaración pública que gobierna.
- Referenciar conceptos compartidos en lugar de redefinirlos para cada entidad.
- Actualizar comentarios cuando cambie el contrato; no mantener garantías que ya no se cumplen.

## Contenido por entidad

| Entidad | Contenido requerido |
|---|---|
| Clases y estructuras | `@brief`, responsabilidad, relaciones, propiedad, vida útil, concurrencia y restricciones pertinentes. |
| Métodos y funciones | `@brief`, `@param`, `@return`, errores, precondiciones y poscondiciones aplicables. |
| Enumeraciones y valores | Significado del dominio y semántica de cada valor público. |
| Alias y constantes | Significado, unidades y límites relevantes. |
| Miembros | Función, rango válido y propiedad cuando formen parte del contrato. |

Utilizar `@details`, `@note` y `@warning` cuando añadan información necesaria.
No generar etiquetas vacías ni garantías inventadas para completar una plantilla.
Documentar complejidad y efectos secundarios cuando afecten al uso correcto de la interfaz.

## Ejemplo

```cpp
/// @brief Vista no propietaria de un identificador.
/// @pre El almacenamiento debe permanecer válido mientras exista la vista.
/// @note Admite consultas concurrentes si los datos observados no cambian.
class Identifier {
public:
    /// @brief Construye la vista sobre almacenamiento válido.
    /// @param wire Dirección no nula del identificador.
    explicit Identifier(const WireIdentifier* wire) noexcept;
};
```

El ejemplo ilustra cómo expresar un contrato; no certifica la semántica de una clase existente.
Las reglas técnicas de propiedad y concurrencia pertenecen a [MEMORY.md](MEMORY.md) y [CONCURRENCY.md](CONCURRENCY.md).

## Verificación

[actor: human | agent] contrasta las afirmaciones con el contrato y la implementación pertinente.
[actor: human | agent | ci] comprueba la sintaxis y generación de documentación con las herramientas adoptadas.
Que Doxygen procese un comentario no demuestra que la garantía descrita sea verdadera.
