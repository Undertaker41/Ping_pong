# Historial de Cambios del Proyecto

Este documento detalla la evolucion y las fases de desarrollo del juego de Ping Pong, desde sus caracteristicas basicas hasta la implementacion de mecanicas avanzadas y correccion de errores.

## Fase 1: Implementacion de la Habilidad Especial

* **Habilidad (Boost):** Se añade la mecanica de "Boost".
    * J1: Tecla `D`.
    * J2: Tecla `Flecha Izquierda`.
* **Efecto:** La velocidad de la paleta aumenta **x1.5**.
* **Visual:** La paleta de J1 se vuelve **Celeste** y la de J2 **Amarilla**.
* **Estamina (v1):**
    * Duracion: 3 segundos.
    * Cooldown (Penalizacion): 3.5 segundos.
    * Regeneracion: 1 a 1 si no se agota.
* **Especificaciones:** Se actualiza la resolucion a **1366x1080** y los FPS a **90**.

## Fase 2: Soporte de Mando y Ajustes de UI

* **UI (Estamina):**
    * Se reduce el tamaño de las barras de estamina.
    * El color de la barra (cuando está disponible) se cambia de verde a los colores respectivos del jugador (Celeste y Amarillo).
* **Menus:**
    * Se añade una nueva pantalla de "Controles" accesible desde el menú de pausa.
* **Controles (Gamepad):**
    * Se implementa la deteccion de mandos de Xbox (J1 y J2).
    * Se añade soporte para movimiento (Joystick Izquierdo y Cruceta) y Boost (botones A, B, X, Y).
    * Se añade navegacion de menu con mando.
* *(Descartado: Se discutio añadir soporte de mouse y re-mapeo de controles, pero se descarto por alta complejidad).*

## Fase 3: Correccion de Bugs (Loop de Juego)

* **Bug Corregido:** El temporizador de la partida y el multiplicador de velocidad no se reiniciaban despues de que un jugador ganara una ronda (alcanzar 12 puntos).
* **UI (Velocidad):** Se elimina el texto "Velocidad:", dejando unicamente el indicador del multiplicador (ej. "x1.2").

## Fase 4: Correccion de Bugs (Controles de Mando)

* **Bug Corregido:** El multiplicador de velocidad no se reiniciaba despues de *cada punto anotado*, solo al final de la ronda. Ahora se reinicia a "x1.0" con cada saque.
* **Bug Corregido (Mando):** Se arregla un error de mapeo de botones:
    * La cruceta (D-pad) pausaba el juego y los botones (A/Y) movian al jugador.
    * *Solucion:* Se mapean correctamente los botones: D-pad/Joystick (Mover), A/B/X/Y (Boost), B (Atras), A (Aceptar).
* **Feature (Mando):** Se añade el boton `Start/Menu` del mando como boton de Pausa.
* **Feature (Mando):** Se permite continuar el juego despues de un punto presionando cualquier boton del mando.

## Fase 5: Balance y "Game Feel"

* **Feature (Menu):** Se añade la capacidad de navegar por los menus usando el Joystick Izquierdo, ademas de la cruceta.
* **Balance (Boost):** La velocidad del Boost se incrementa de x1.5 a **x2.0**.
* **Balance (Estamina):** La duracion maxima de la estamina se reduce a la mitad (de 3.0s a **1.5s**).
* **Feature (Coyote Time):** Se añade un "Tiempo Coyote": un bufer de **5 pixeles** por encima y por debajo de la paleta para hacer los golpes mas permisivos.

## Fase 6: Pulido Final y Balance

* **Balance (Coyote Time):** Se refina la mecanica. El bufer de 5 pixeles ahora solo se activa si el jugador esta **moviendose activamente**. Si esta quieto, el golpe debe ser preciso.
* **Balance (Estamina):** El cooldown de penalizacion (al agotar la barra) se reduce de 3.5s a **2.8s**.
* **Bug Corregido:** La estamina y su cooldown no se reiniciaban al anotar un punto.
    * *Solucion:* Ahora, la estamina de ambos jugadores se restaura completamente a `MAX_STAMINA` despues de cada punto, al igual que el timer y el multiplicador.

## Fase 7: Movimiento Analogico y Super Boost (v0.70)

* **Feature (Mando):** El movimiento con Joystick Izquierdo ahora es **analogico**, permitiendo control de velocidad variable.
* **Feature (Habilidad):** Se añade el **"Super Boost" (Dash)** en un boton separado.
    * J1: Tecla `A`, Mando `B/Y`.
    * J2: Tecla `Flecha Derecha`, Mando `B/Y`.
* **Feature (Habilidad):** El Boost Normal se mapea a J1 (`D`, Mando `A/X`) y J2 (`Flecha Izq`, Mando `A/X`).
* **UI:** Se implementa **transicion de color suave (Lerp)** para las paletas al entrar y salir del modo boost.
* **UI:** Se añade un **flash Amarillo "potente"** al activar el Super Boost para una sensacion mas impactante.
* **Balance (Estamina):** Se re-balancea la estamina (1.0s de gasto, penalizaciones ajustadas).

## Fase 8: Re-balance de Combate y Entorno (v0.80)

* **Balance (Combate):** Golpear la pelota mientras se usa Boost (Normal o Super) ahora consume un **15%** de la barra de estamina instantaneamente.
* **Balance (Combate):** La fisica de la pelota al ser golpeada con boost es mas **impredecible** (rango de angulo Y aumentado).
* **Balance (Estamina):** Se re-ajustan los tiempos de recarga:
    * Recarga Normal: **20% mas lento** que el gasto (1.2s total).
    * Penalizacion (al agotar): **50% mas lento** que el gasto (1.5s total).
* **UI:** El color de fondo del juego se cambia a un **azul marino oscuro**.
* **Feature:** El juego ahora carga un archivo `icon.png` para la ventana y la barra de tareas.
* **Bug Corregido:** Se corrige un crasheo (`UnboundLocalError`) que ocurria al pausar el juego antes de que la logica de color se ejecutara.

## Fase 9: Mecanica de Cargas y IA Avanzada (v0.90)

* **Balance (Super Boost):** La mecanica de Super Boost se cambia a un sistema de **3 Cargas** (cada toque consume 33.3% de estamina).
* **Feature (Super Boost):** El dash se re-balancea para ser un "blink" (velocidad **x7.5** por 0.08s).
* **Feature (Super Boost):** Se añade un **"Margen de Golpe"** (20ms) que permite que la fisica de boost se aplique "casi perfecto" (pixel perfect) despues de que el dash termina.
* **Feature (IA):** La IA en modo **Extremo** ahora puede usar Boost Normal y Super Boost para defender, gestionando su propia barra de estamina.
* **Refactor:** El codigo de logica de juego en `modelo.py` se re-estructura visualmente con comentarios para separar la logica "Basica" de las mecanicas "Avanzadas".
* **UI:** Se añade un indicador de version (**v0.90**) en las pantallas del menu principal.

## Fase 10: Pulido Visual (v0.91)

* **Feature (Visual):** Se añade una "estela" (paddle trail) a las paletas de los jugadores y de la IA cuando activan cualquier modo de boost (Normal o Super Boost), similar a la estela de la pelota.
* **UI:** Se actualiza la version a **v0.91**.

## Fase 11: Refactor a Modelo-Vista-Controlador (v0.95)

* **Refactor (Arquitectura):** El proyecto entero se re-escribe para seguir un patron de diseño **Modelo-Vista-Controlador (MVC)**.
    * **`main.py`:** Se convierte en el punto de entrada que inicializa los componentes y corre el bucle principal.
    * **`modelo.py`:** Ahora solo contiene el estado (`GameState`) y la logica pura del juego. No tiene codigo de Raylib para inputs o dibujado.
    * **`vista.py`:** Nuevo archivo que maneja toda la inicializacion de la ventana y el dibujado (todas las llamadas a `rl.draw_...`).
    * **`controlador.py`:** Nuevo archivo que maneja toda la logica de inputs (teclado y gamepad) y los traduce para el modelo.
* **UI:** Se actualiza la version a **v0.95**.