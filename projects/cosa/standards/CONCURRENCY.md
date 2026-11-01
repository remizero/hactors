# Concurrencia y sincronización: perfil C++

## Alcance

[actor: human | agent] aplica estas reglas a código concurrente, IPC y ejecución asíncrona.
Las garantías deben figurar en los contratos conforme a [DOCUMENTATION.md](DOCUMENTATION.md).

## Estado compartido

- Declarar si cada interfaz admite lectura concurrente, mutación concurrente o uso exclusivo.
- Preferir mensajes, estado por hilo o proceso y datos inmutables tras su publicación.
- La publicación de datos inmutables debe establecer la sincronización y vida útil necesarias.
- La lectura concurrente de datos correctamente publicados e inmutables no requiere bloquear por cada lectura.
- Los constructores mutables y acumuladores no son seguros para uso concurrente salvo contrato explícito; usar una instancia por hilo.

## Bloqueos

- Gestionar mutex mediante `std::lock_guard`, `std::unique_lock` o `std::scoped_lock`.
- No invocar directamente `lock()` o `unlock()` sobre el mutex.
- Definir una jerarquía global al adquirir varios bloqueos.
- Mantener corta la sección crítica.
- No ejecutar callbacks externos ni E/S bloqueante mientras se mantiene un mutex.

## Operaciones atómicas

- Usar `std::atomic<T>` para banderas, contadores y punteros cuando su protocolo sea realmente atómico.
- Especificar el orden de memoria y justificar los órdenes distintos de `seq_cst`.
- No asumir que operaciones atómicas individuales hacen atómica una secuencia compuesta.
- Mantener la propiedad y recuperación de los objetos observados por punteros atómicos.

## Ejecución asíncrona

- Integrar E/S de red, IPC y disco en el modelo asíncrono definido para el componente.
- No bloquear un hilo trabajador esperando la finalización de E/S.
- Una API de disco bloqueante no se vuelve no bloqueante por llamarla desde un bucle de eventos; una adaptación necesita diseño explícito.
- Preferir colas SPSC o MPSC sin bloqueos en rutas IPC críticas cuando correspondan al número real de productores y consumidores.
- No elegir una estructura sin bloqueos si su contrato de concurrencia no coincide con el uso.

## Verificación

[actor: human | agent | ci] ejecuta las pruebas y analizadores de [TESTING.md](TESTING.md).
Las pruebas deben ejercer las transiciones y concurrencia del contrato, no depender de pausas arbitrarias para aparentar sincronización.
Los presupuestos temporales y costes de sincronización se rigen por PERFORMANCE.md, sin proveedor en esta composición del perfil conforme a [MEMORY.md](MEMORY.md#alcance).
