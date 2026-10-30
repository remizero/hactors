<!-- schema: rfc/1.0 -->

# Plantilla RFC-F — Feature

[actor: human | agent] completa esta plantilla siguiendo [RFC.md](../RFC.md).
Los campos vacíos son información por resolver, no criterios satisfechos.
Los estados y autorizaciones proceden de [LIFECYCLE.md](../LIFECYCLE.md).

## Metadatos y cuerpo común

Completar los metadatos y el cuerpo común conforme a [RFC_TEMPLATE.md](RFC_TEMPLATE.md).
`type` debe ser `"F"` (Feature).
Esta plantilla añade únicamente las secciones específicas del tipo.

## Campos específicos

```yaml
follow_up_rfcs: []
```

### Secciones específicas de feature

**follow_up_rfcs:** RFCs de seguimiento propuestas; cada una con tipo, propósito y relación `derives` con esta RFC-F.

## Pruebas y documentación de seguimiento

Al completar la feature, [actor: human | agent] propone:

1. **RFC-T** para pruebas de verificación si la feature introduce mecanismos de seguridad, composición o propiedades que requieren validación independiente.
2. **RFC-D** para documentación si la feature afecta arquitectura, contratos públicos o superficies visibles.

Cada RFC propuesta conserva su identificador y relación `derives` con esta RFC-F.
La RFC-T propuesta no es obligatoria; se justifica su ausencia si la feature no introduce propiedades verificables independientes.
La RFC-D propuesta no es obligatoria; se justifica su ausencia si la feature no afecta documentación existente ni requiere consolidación.

## Resumen y continuidad

Al completar la feature, [actor: human | agent] redacta un resumen conforme a [SUMMARY_TEMPLATE.md](SUMMARY_TEMPLATE.md).
El resumen sintetiza arquitectura, contratos, migración, pruebas y RFCs de seguimiento propuestas.
Las RFCs de seguimiento pueden ejecutarse en paralelo o secuencia; cada una conserva su ciclo de vida independiente.
