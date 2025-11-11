# Historial de Cambios del Proyecto

Este documento detalla la evolución y las fases de desarrollo del juego de Ping Pong, desde sus características básicas hasta la implementación de mecánicas avanzadas y corrección de errores.

## Fase 1: Implementación de la Habilidad Especial

* **Habilidad (Boost):** Se añade la mecánica de "Boost".
    * J1: Tecla `D`.
    * J2: Tecla `Flecha Izquierda`.
* **Efecto:** La velocidad de la paleta aumenta **x1.5**.
* **Visual:** La paleta de J1 se vuelve **Celeste** y la de J2 **Amarilla**.
* **Estamina (v1):**
    * Duración: 3 segundos.
    * Cooldown (Penalización): 3.5 segundos.
    * Regeneración: 1 a 1 si no se agota.
* **Especificaciones:** Se actualiza la resolución a **1366x1080** y los FPS a **90**.

## Fase 2: Soporte de Mando y Ajustes de UI

* **UI (Estamina):**
    * Se reduce el tamaño de las barras de estamina.
    * El color de la barra (cuando está disponible) se cambia de verde a los colores respectivos del jugador (Celeste y Amarillo).
* **Menús:**
    * Se añade una nueva pantalla de "Controles" accesible desde el menú de pausa.
* **Controles (Gamepad):**
    * Se implementa la detección de mandos de Xbox (J1 y J2).
    * Se añade soporte para movimiento (Joystick Izquierdo y Cruceta) y Boost (botones A, B, X, Y).
    * Se añade navegación de menú con mando.
* *(Descartado: Se discutió añadir soporte de mouse y re-mapeo de controles, pero se descartó por alta complejidad).*

## Fase 3: Corrección de Bugs (Loop de Juego)

* **Bug Corregido:** El temporizador de la partida y el multiplicador de velocidad no se reiniciaban después de que un jugador ganara una ronda (alcanzar 12 puntos).
* **UI (Velocidad):** Se elimina el texto "Velocidad:", dejando únicamente el indicador del multiplicador (ej. "x1.2").

## Fase 4: Corrección de Bugs (Controles de Mando)

* **Bug Corregido:** El multiplicador de velocidad no se reiniciaba después de *cada punto anotado*, solo al final de la ronda. Ahora se reinicia a "x1.0" con cada saque.
* **Bug Corregido (Mando):** Se arregla un error de mapeo de botones:
    * La cruceta (D-pad) pausaba el juego y los botones (A/Y) movían al jugador.
    * *Solución:* Se mapean correctamente los botones: D-pad/Joystick (Mover), A/B/X/Y (Boost), B (Atrás), A (Aceptar).
* **Feature (Mando):** Se añade el botón `Start/Menu` del mando como botón de Pausa.
* **Feature (Mando):** Se permite continuar el juego después de un punto presionando cualquier botón del mando.

## Fase 5: Balance y "Game Feel"

* **Feature (Menú):** Se añade la capacidad de navegar por los menús usando el Joystick Izquierdo, además de la cruceta.
* **Balance (Boost):** La velocidad del Boost se incrementa de x1.5 a **x2.0**.
* **Balance (Estamina):** La duración máxima de la estamina se reduce a la mitad (de 3.0s a **1.5s**).
* **Feature (Coyote Time):** Se añade un "Tiempo Coyote": un búfer de **5 píxeles** por encima y por debajo de la paleta para hacer los golpes más permisivos.

## Fase 6: Pulido Final y Balance

* **Balance (Coyote Time):** Se refina la mecánica. El búfer de 5 píxeles ahora solo se activa si el jugador está **moviéndose activamente**. Si está quieto, el golpe debe ser preciso.
* **Balance (Estamina):** El cooldown de penalización (al agotar la barra) se reduce de 3.5s a **2.8s**.
* **Bug Corregido:** La estamina y su cooldown no se reiniciaban al anotar un punto.
    * *Solución:* Ahora, la estamina de ambos jugadores se restaura completamente a `MAX_STAMINA` después de cada punto, al igual que el timer y el multiplicador.