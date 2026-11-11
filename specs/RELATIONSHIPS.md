# Relaciones entre artefactos

## Alcance

Define la relación como concepto: su forma, su dirección, los extremos que admite, sus restricciones y su ciclo de vida.

La **representación** de una relación en el grafo del proyecto y la correspondencia entre cada campo documental y su arista pertenecen a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relaciones-del-proyecto); no se redefinen aquí. El **significado** de cada tipo lo fija la especificación del artefacto que lo declara, recogida en la tabla de vocabulario. Esta tabla no añade requisitos: cuando una entrada discrepe de su especificación, prevalece aquella.

## Forma

Una relación es una terna direccional:

```yaml
- source: RFC-A00001
  target: RFC-A00001-F00001
  relation: derives
```

- `source` y `target` identifican artefactos conforme a [DEFINITIONS.md](DEFINITIONS.md#nomenclatura).
- `relation` usa exclusivamente un valor del vocabulario siguiente, en la dirección que su especificación fija.
- La relación es direccional: no se escribe la inversa salvo que sea otra relación con su propio tipo.

En la lista `relations:` de un documento el origen es implícito y es el propio documento, así que un documento no puede declarar una arista en la que él sea el destino. Esa arista la declara el documento del otro extremo; la excepción es `supersedes`, cuya traducción produce la misma arista desde cualquiera de los dos campos, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relaciones-del-proyecto).

## Vocabulario

| Relación | Dirección | Especificación |
|---|---|---|
| `derives` | RFC de origen → RFC derivada. | [RFC.md](RFC.md#relaciones) |
| `depends-on` | Artefacto dependiente → artefacto requerido. | [RFC.md](RFC.md#relaciones) |
| `informs` | Fuente de información → artefacto informado; no bloquea por sí misma. | [RFC.md](RFC.md#relaciones) |
| `validated-by` | Artefacto objeto de validación → artefacto que define esa validación. | [RFC.md](RFC.md#relaciones) |
| `supersedes` | Sucesor → sustituido, sin borrarlo. | [RFC.md](RFC.md#relaciones) |
| `supports` | Evidencia → afirmación concreta del artefacto que respalda. | [EVD_TEMPLATE.md](templates/EVD_TEMPLATE.md#relaciones-de-aplicabilidad) |
| `affects` | Hallazgo → artefacto afectado. | [FND_TEMPLATE.md](templates/FND_TEMPLATE.md#relaciones-de-afectación) |
| `derived_from` | Artefacto derivado → su antecedente: identidad HRN → versión exacta del HRN antecedente, o TEST → TEST antecedente. | [HRN_TEMPLATE.md](templates/HRN_TEMPLATE.md#relaciones), [TESTS.md](TESTS.md#relaciones) |
| `compatible_with` | Versión exacta de HRN → TEST o versión exacta de otro HRN. | [HRN_TEMPLATE.md](templates/HRN_TEMPLATE.md#relaciones) |
| `uses` | TEST → `HRN-nnnnn@vNNN` reutilizada; solo existe en el grafo. | [HARNESS.md](HARNESS.md#origen-pertenencia-y-reutilización) |

Un tipo nuevo exige definir su dirección y su especificación antes de declararlo; no se deduce del nombre ni se usa como sinónimo de otro.

## Extremos admitidos

Los dos extremos son artefactos. Una instancia de ejecución no lo es, y su vínculo con lo que ejecuta ya lo registra su `identity`, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relaciones-del-proyecto): la contención no produce aristas y no se representa como relación.

Un `target` puede llevar un fragmento `#<identificador>` cuando el vínculo es con un criterio u objetivo dentro del artefacto. Un `target` ajeno al proyecto debe identificar también el proyecto propietario, como en [HRN_TEMPLATE.md](templates/HRN_TEMPLATE.md#identidad), y no se resuelve dentro de este.

No hay referencias tipadas ni localizadores de texto libre: un extremo o identifica un artefacto o no es un extremo. Un módulo, un defecto de un rastreador externo o un documento de análisis se vinculan declarando el artefacto del proyecto que los representa —una RFC, un hallazgo, una decisión o una evidencia—, no mediante un sustituto de identidad.

## Restricciones

- `depends-on` no admite ciclos. Un ciclo detectado bloquea la transición afectada y su resolución es disposición `[actor: human]`: retirar una dependencia o reducir un alcance.
- `supersedes` exige que el sustituido declare `superseded_by` hacia su sucesor en su propio documento; los dos campos producen una sola arista.
- Una relación no confiere autoridad: de ninguna se infiere aprobación, dependencia de ejecución ni cierre, conforme a [RFC.md](RFC.md#relaciones) y a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#derivación-documental-y-contención-de-ejecuciones).
- `supports` no transfiere aplicabilidad de un criterio a otro ni de una revisión a otra, conforme a [EVIDENCE.md](EVIDENCE.md).
- `affects` no atribuye al origen la causa del defecto ni convierte al artefacto de origen en afectado, que debe declararse explícitamente, conforme a [FINDING.md](FINDING.md).
- La terna no se duplica: dos documentos que declaran la misma relación desde extremos distintos producen una sola arista, y `hactors relate` rechaza una idéntica ya registrada.

## Ciclo de vida de una arista

Una arista declarada no se borra silenciosamente: se sustituye por otra con `supersedes` hacia su reemplazo, o su retiro se documenta en el artefacto que la declaraba. Las relaciones derivadas de hallazgos resueltos o de decisiones sustituidas permanecen como antecedente histórico, igual que los artefactos rechazados, cancelados o sustituidos no se eliminan por defecto, conforme a [LIFECYCLE.md](LIFECYCLE.md#rechazo-sustitución-y-cancelación).

## Consistencia

Toda relación documental debe representarse en el grafo del proyecto dentro de la misma operación que crea o modifica el artefacto que la produce, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relaciones-del-proyecto).

`hactors validate` comprueba la resolución de cada `target` y la completitud de las aristas que la tabla de traducción produce; no resuelve `source`, no resuelve el fragmento de un `target`, no valida `relation` contra este vocabulario ni denuncia una arista que ningún documento declare, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#grafo-del-proyecto). Lo que la comprobación deja fuera sigue siendo responsabilidad de quien declara la relación.

Una discrepancia se resuelve desde la fuente con autoridad: el documento aprobado sobre su representación en el grafo. El grafo no es una segunda fuente capaz de desmentir al documento, ni una vista lo es de ninguno de los dos, conforme a [VIEWS.md](VIEWS.md).

## Consultas mínimas

[actor: human | agent] debe poder responder a partir del grafo y de los documentos:

- ¿De qué deriva este artefacto y qué deriva de él?
- ¿Qué debe avanzar antes de que este pueda hacerlo?
- ¿Qué evidencia respalda cada afirmación, y a qué afirmación concreta?
- ¿Qué hallazgos afectan a este artefacto?
- ¿Qué artefacto fue sustituido y por cuál?
