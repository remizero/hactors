<!-- schema: rfc/1.0 -->

# Plantilla RFC-D — Documentación

[actor: human | agent] completa esta plantilla siguiendo [RFC.md](../RFC.md).
Los campos vacíos son información por resolver, no criterios satisfechos.
Los estados y autorizaciones proceden de [LIFECYCLE.md](../LIFECYCLE.md).

## Metadatos y cuerpo común

Completar los metadatos y el cuerpo común conforme a [RFC_TEMPLATE.md](RFC_TEMPLATE.md).
`type` debe ser `"D"` (Documentación).
Esta plantilla añade únicamente las secciones específicas del tipo.

## Campos específicos

```yaml
documentation_layers: []
content_minimum: []
traceability: ""
verification: ""
```

### Secciones específicas de documentación

**documentation_layers:** capas documentales afectadas; para cada una: contenido, exclusión, responsable.

**content_minimum:** contenido mínimo requerido; cada ítem con sección, propósito y criterio de completitud.

**traceability:** cómo se trazan las garantías documentadas a contratos responsables y pruebas que las ejercitaron.

**verification:** cómo se verifica la coherencia documental: enlaces, referencias de código, estados de RFC, diagramas, markup.

## Restricciones

- NO modificar código, tests, CI, cuentas, permisos ni despliegue.
- NO promover RFC drafts a decisiones aprobadas.
- NO aceptar seguridad en nombre del usuario.
- NO editar la RFC fuente por iniciativa propia.
- NO completar documentos deliberadamente vacíos sin autorización específica.
- La documentación no puede subsanar una garantía que los tests no demostraron: registra la limitación y la RFC pendiente, sin afirmar cierre global.

## Calidad documental

- SRP: documentación de la arquitectura comprobada.
- GRASP: información técnica validada con su dueño.
- Clean Code aplicado a documentación: términos únicos, ejemplos ejecutables cuando corresponda, enlaces precisos y separación entre hechos y aspiraciones.
- No introducir un glosario que contradiga las APIs reales.

## Resumen y continuidad

Al completar la documentación, [actor: human | agent] redacta un resumen conforme a [RFC_SUMMARY.md](RFC_SUMMARY.md).
El resumen sintetiza qué se actualizó, qué garantías tiene evidencia y cuáles siguen pendientes.
No un nuevo framework documental ni otra copia de todas las RFC.
