# Fundamentos de ingeniería.

## Alcance

Estos fundamentos rigen SPECS con independencia del lenguaje, proyecto o ejecutor.
[actor: human | agent] debe aplicarlos al proponer, implementar, documentar y verificar cambios.
La automatización ejecuta el mismo proceso; no constituye una metodología alternativa.
Las particularidades arquitectónicas las declara cada proyecto y no forman parte de SPECS.
Los términos empleados se definen en [DEFINITIONS.md](DEFINITIONS.md).

## Contratos explícitos y estables

- Definir y validar interfaces, semántica, garantías y límites antes de implementar.
- Permitir sustituir implementaciones sin alterar los contratos de sus consumidores.
- No cambiar contratos ni arquitectura como efecto secundario de una tarea.
- Hacer explícitas las dependencias, la propiedad de recursos y las transiciones de estado.

## Responsabilidades y composición

- Asignar una responsabilidad coherente a cada componente y documento.
- Preferir composición a jerarquías de herencia profundas.
- Separar dominio e infraestructura; depender de abstracciones y no de detalles internos ajenos.
- Segregar interfaces para que cada consumidor dependa solo de lo que necesita.
- Mantener componentes pequeños, cohesionados, comprensibles y comprobables localmente.
- Evitar estado compartido y retener estado solo donde exista una responsabilidad explícita sobre él.

## Simplicidad y evolución

- Preferir soluciones claras y predecibles a complejidad innecesaria.
- No introducir abstracciones, dependencias o extensiones para necesidades hipotéticas.
- Avanzar mediante incrementos pequeños, funcionales y verificables.
- Elegir diseños que puedan evolucionar, sin bloquear el progreso buscando perfección anticipada.
- Conservar las razones de las decisiones y sus alternativas relevantes.

## Seguridad y recursos

- Aplicar mínimo privilegio y valores predeterminados restrictivos.
- Validar entradas y autorizaciones antes de producir efectos protegidos.
- Detectar y comunicar errores cerca de su origen; no ocultar fallos ni inventar resultados.
- Definir adquisición, transferencia y liberación de recursos durante todo su ciclo de vida.
- Hacer explícitas las garantías de concurrencia, recuperación y parada de cada componente.

## Comportamiento verificable

- Precisar el comportamiento esperado para las entradas y estados contemplados por el contrato.
- Diseñar interfaces y dependencias que permitan verificar ese comportamiento.
- Vincular cada objetivo con criterios de aceptación observables.
- Distinguir implementación, ejecución de pruebas, resultados y validación de criterios.
- Hacer observable la ejecución sin cambiar su semántica funcional.
- Definir y medir las garantías temporales cuando sean parte del contrato.

## Conocimiento y documentación

- Mantener una definición normativa por concepto; referenciarla en lugar de redefinirla.
- Separar reglas, fundamentos y ejemplos: un ejemplo no añade obligaciones implícitas.
- Construir el contexto con las dependencias necesarias antes de actuar, según INDEX_SPECS.md.
- Declarar supuestos y resolver contradicciones antes de basar cambios en ellos.
- Mantener sincronizados los contratos documentados y los cambios que los afectan.
- Conservar la historia sin confundirla con el estado vigente; la autoridad de cada artefacto se define en [ARTIFACTS.md](ARTIFACTS.md).

## Gobierno del trabajo

- Proponer y aprobar cambios significativos antes de implementarlos.
- Revisar y verificar antes de integrar; no sustituir evidencia por una declaración de cumplimiento.
- Limitar cada tarea al alcance autorizado y preservar el trabajo ajeno.
- Aplicar las responsabilidades y transiciones de WORKFLOW.md y de [LIFECYCLE.md](LIFECYCLE.md).
- La autoría humana o automatizada no cambia los criterios de calidad ni concede autoridad adicional.

## Referencias de diseño

La encapsulación, SOLID, GRASP y el código legible orientan estos fundamentos.
Las filosofías UNIX y MINIX inspiran la composición y el aislamiento que SPECS exige a todo proyecto.
Estas referencias explican el diseño; no importan automáticamente todas las reglas de esas escuelas.
