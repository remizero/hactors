<!-- schema: test/1.0 -->

# Plantilla de TEST

[actor: human | agent] redacta un TEST cuando una verificación necesita identidad propia: una propiedad bajo comprobación con criterios que deciden si se cumple.
Su contenido y su propósito son inmutables; las reglas de identidad, inmutabilidad y relaciones están en [TESTS.md](../TESTS.md).
Su autoridad como artefacto está en [ARTIFACTS.md](../ARTIFACTS.md).

## Identidad

```yaml
id: TEST-nnnnn
title: ""
origin: ""
date: ""
proposed_by: ""
```

| Campo | Descripción |
|---|---|
| `id` | `TEST-nnnnn` único en el proyecto; no se reutiliza al retirar. |
| `title` | Descripción concisa de la propiedad que se verifica. |
| `origin` | Artefacto que motivó la creación del TEST, normalmente una RFC. Se conserva históricamente y no cambia con el contexto de cada ejecución. |
| `date` | `YYYY-MM-DD` de creación. |
| `proposed_by` | Autoría del TEST; no implica aprobación de ningún resultado. |

## Cuerpo

```yaml
property: ""
criteria: []
procedure: []
out_of_scope: []
relations: []
references: []
```

### Secciones

**property:** propiedad bajo verificación, enunciada de forma que su cumplimiento sea decidible.

**criteria:** condiciones que deciden el resultado; cada una con identificador estable para que una evidencia pueda respaldarla por separado.

**procedure:** pasos que producen el resultado, en orden; referencias a los archivos del sistema documentado que los realizan y a las `HRN-nnnnn@vNNN` que se reutilicen.

**out_of_scope:** comportamientos deliberadamente excluidos; reutilizar el TEST para uno de ellos exige un TEST nuevo.

**relations:** entradas con `target` y `relation`; el origen es el propio TEST, que no se repite en cada vínculo. Solo `derived_from` hacia el TEST antecedente.

**references:** fuentes consultadas: RFC, hallazgos, ADR, evidencias.

## Ubicación

El documento vive en la raíz del proyecto, en `projects/<proyecto>/tests/TEST-nnnnn.md`, con su `id:` en un bloque `yaml`. No se busca en ningún otro nivel ni dentro del árbol de instancias: el vínculo con la RFC de cada ejecución lo declara la instancia, no su ruta.
Su instancia de ejecución `test_run` vive dentro del `rfc_run` correspondiente y referencia el documento sin copiar sus criterios ni su procedimiento. La jerarquía, su ruta activa y su creación se definen en [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md).

## Restricciones

- No modificar el contenido ni el propósito para satisfacer otro objetivo: se crea un TEST nuevo con `derived_from` hacia el antecedente.
- No declarar en el documento un resultado, una plataforma observada ni una revisión examinada: pertenecen a la evidencia de cada ejecución, conforme a [EVIDENCE.md](../EVIDENCE.md).
- No afirmar que un criterio se cumple por existir el documento; lo acredita una EVD ligada a su ejecución.
- Un TEST no declara campo `actions:`: las acciones que su ejecución motiva se registran en la RFC correspondiente.
