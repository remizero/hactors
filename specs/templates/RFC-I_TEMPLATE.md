<!-- schema: rfc/1.0 -->

# Plantilla RFC-I — Integración

[actor: human | agent] completa esta plantilla siguiendo [RFC.md](../RFC.md).
Los campos vacíos son información por resolver, no criterios satisfechos.
Los estados y autorizaciones proceden de [LIFECYCLE.md](../LIFECYCLE.md).

## Metadatos y cuerpo común

Completar los metadatos y el cuerpo común conforme a [RFC_TEMPLATE.md](RFC_TEMPLATE.md).
`type` debe ser `"I"` (Integración).
Esta plantilla añade únicamente las secciones específicas del tipo.

## Campos específicos

```yaml
preconditions: []
composition: ""
adoption: ""
affected_files: []
integration_tests: ""
```

### Secciones específicas de integración

**preconditions:** prerrequisitos de entrada; contratos y arquitecturas aprobados de las features que se integran; matriz de trust classes, recursos y derechos aprobada.

**composition:** composición y flujo de la integración; diagramas, responsabilidades, handoffs, coordinación.

**adoption:** adopción de módulos existentes; qué interfaces se adaptan o sustituyen, migración, dependencias.

**affected_files:** archivos y fronteras afectadas; rutas candidatas, límites de modificación, exclusiones.

**integration_tests:** pruebas de integración; ruta productiva real en fixture, controles positivos y negativos, fault injection.

## Restricciones

- NO crear otro módulo que duplique funcionalidad existente.
- NO implementar mecanismos ausentes en las features; si falta una garantía, devolverla a su RFC propietario.
- NO resolver hallazgos modificando un helper o retirando su aserción.
- Integrar solo después de que las features previas ofrezcan todas las capacidades necesarias.

## Calidad y decisiones abiertas

- SRP: ensamblaje de contratos, no nuevas políticas.
- GRASP Controller: los módulos coordinan sus casos de uso; Information Expert permanece en cada subsistema.
- DIP: interfaces y valores, no dependencia circular entre implementaciones.

Listar decisiones abiertas (UNRESOLVED) y dónde quedaron resueltas o dónde deben resolverse.

## Resumen y continuidad

Al completar la integración, [actor: human | agent] redacta un resumen conforme a [SUMMARY_TEMPLATE.md](SUMMARY_TEMPLATE.md).
El resumen sintetiza composición, adopción, pruebas de integración y decisiones abiertas.
La integración prepara la ruta para RFC-T de verificación; esa RFC-T conserva su ciclo de vida independiente.
