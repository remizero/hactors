<!-- schema: rfc/1.0 -->

# Plantilla RFC-T — Tests

[actor: human | agent] completa esta plantilla siguiendo [RFC.md](../RFC.md).
Los campos vacíos son información por resolver, no criterios satisfechos.
Los estados y autorizaciones proceden de [LIFECYCLE.md](../LIFECYCLE.md).

## Metadatos y cuerpo común

Completar los metadatos y el cuerpo común conforme a [RFC_TEMPLATE.md](RFC_TEMPLATE.md).
`type` debe ser `"T"` (Tests).
Esta plantilla añade únicamente las secciones específicas del tipo.

## Campos específicos

```yaml
property_under_test: ""
fixture: ""
stimuli: []
security_matrix: []
regressions: ""
ownership: ""
evidence: ""
```

### Secciones específicas de tests

**property_under_test:** propiedad que se verifica; qué invariantes, garantías o comportamientos se miden.

**fixture:** descripción del fixture: componentes, configuración, recursos temporales, telemetría.

**stimuli:** estímulos de prueba: casos positivos y negativos, precondiciones, oráculos mínimos.

**security_matrix:** matriz de seguridad (si aplica); cada caso con estímulo, frontera, observación externa y límite de su conclusión.

**regressions:** adaptaciones explícitas de tests existentes; qué propiedad conservan, qué sujeto cambia, cómo se preservan intenciones.

**ownership:** ownership y dependencias; qué módulos se consumen, qué superficies se observan, qué autoridades no se crean.

**evidence:** evidencia y reproducción; revisión, árbol, plataforma, comandos literales, retornos, duración, resultados por caso.

## Restricciones

- NO implementar mecanismos de seguridad.
- NO cambiar perfiles para acomodar resultados.
- NO sustituir OS/autoridad por mocks en la evidencia final.
- NO convertir un bypass observado en éxito esperado.
- Un defecto productivo encontrado se informa y se deriva a su RFC/fix; no se arregla silenciosamente dentro de este encargo de tests.

## Calidad

- SRP: verificar una propiedad compuesta, no construir su enforcement.
- DIP: consumir las superficies productivas; los dobles pueden servir para fault injection localizada, nunca sustituir el OS en la evidencia final.
- GRASP: cada observación proviene del dueño correspondiente.
- Clean Code: fixtures deterministas, nombres por propiedad, errores que distinguen fallo de infraestructura de fallo del oráculo.

## Resumen y continuidad

Al completar las pruebas, [actor: human | agent] redacta un resumen conforme a [SUMMARY_TEMPLATE.md](SUMMARY_TEMPLATE.md).
El resumen sintetiza propiedad bajo prueba, fixture, matriz de seguridad, resultados y límites de plataforma.
No modificar la RFC fuente del usuario, reescribir evidencias históricas ni declarar superseded por iniciativa del harness.
