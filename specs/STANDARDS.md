# Estándares y perfiles técnicos

## Alcance

Los estándares concretan los [fundamentos](FOUNDATIONS.md) para los perfiles técnicos que componga cada proyecto.

Un perfil no es una norma de HACTORS. Los documentos que lo componen pertenecen al `standards/` del proyecto que los liga, conforme a [PROJECTS.md](PROJECTS.md#estructura-de-un-proyecto-hactors) y a [CONTEXT_LOADING.md](CONTEXT_LOADING.md#documentos-de-proyecto). Ningún paquete es obligatorio para todo proyecto y ninguno se copia a `specs/`.

[actor: human | agent] aplica los estándares que la composición del proyecto active. Esta norma no los enumera, porque cada proyecto compone los suyos y HACTORS no puede conocerlos de antemano.

## Responsabilidad de cada estándar

| Dominio de regla | Reglas que define |
|---|---|
| Lenguaje | Lenguaje, compiladores, errores y estructura de código. |
| Nombres | Nombres de entidades y archivos. |
| Memoria | Propiedad, vida de recursos, vistas y representación binaria. |
| Concurrencia | Sincronización, hilos y ejecución asíncrona. |
| Rendimiento | Rutas críticas, memoria y presupuestos de rendimiento. |
| Pruebas | Convenciones técnicas de pruebas. |
| Documentación | Contratos documentados y comentarios en código. |
| Control de versiones | Operaciones de control de versiones y publicación. |
| Formato | Configuración y aplicación del formato. |

La tabla identifica dominios que la composición del proyecto debe tener cubiertos; no declara dónde vive cada documento ni qué capa lo aporta. Esa asignación la hace la composición del proyecto, y un dominio sin proveedor en ella es un vacío que [CONTEXT_LOADING.md](CONTEXT_LOADING.md) no puede cargar en silencio. Las condiciones de carga pertenecen únicamente a ese índice.

## Excepciones y cambios

- [actor: human | agent] identifica la regla afectada, la necesidad de desviarse y sus consecuencias.
- [actor: human] aprueba la excepción antes de aplicarla, conforme a [EXCEPTIONS.md](EXCEPTIONS.md).
- [actor: human | agent] registra la decisión en el `decisions/` del proyecto, conforme a [DECISIONS.md](DECISIONS.md), con alcance y comprobaciones.
- [actor: human | agent] no interpreta un ejemplo, una limitación de herramienta o código antiguo como excepción implícita.

Un estándar no puede alterar silenciosamente un contrato público ni las restricciones de una RFC aprobada.

Un estándar que contradiga esta copia normativa no la sustituye: prevalece `specs/`, y la desviación que el proyecto necesite se registra como excepción explícita con su alcance y su límite.

La adopción de otro lenguaje amplía o sustituye el perfil técnico del proyecto, sin reescribir el proceso común de [WORKFLOW.md](WORKFLOW.md).
