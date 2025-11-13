# Proyecto: Ping Pong Avanzado (v0.96 Funcional)

Este es un juego clasico de Ping Pong desarrollado en Python y Raylib, una IA desafiante, y soporte completo para multijugador local y mandos de Xbox.

## 🚀 Caracteristicas Principales

* **Graficos Fluidos:** Corre a 1366x768p y 90 FPS.
* **Modos de Juego:** Juega solo contra la IA o en multijugador local (J1 vs J2).
* **IA Desafiante:** Multiples niveles de dificultad, incluyendo un modo "Extremo (Jaque Mate)" que ahora puede usar habilidades especiales.
* **Habilidades Avanzadas:** Un sistema de combate que incluye un **Boost** (mantener) y un **Super Boost** (dash de 3 cargas).
* **Soporte Completo de Mando:** Deteccion automatica de mandos de Xbox (o compatibles) con movimiento analogico y controles completos en menus.
* **Mecanicas de "Game Feel":**
    * **Tiempo Coyote:** Un pequeño bufer de 5 pixeles que te permite golpear la bola aunque no estes perfectamente alineado, *solo si te estas moviendo*.
    * **Velocidad Progresiva:** La bola aumenta su velocidad (multiplicador) cuanto mas dura el punto.
    * **Transicion de Color (Lerp):** Las paletas cambian de color suavemente al usar habilidades.
    * **Estelas (Trails):** La pelota y las paletas dejan una estela visual al moverse con boost.
* **Historial de Partidas:** El juego guarda automaticamente los resultados de las partidas en un archivo `historial.txt`.
* **Icono Personalizado:** El juego carga un `icon.png` para la ventana y la barra de tareas.

---

## 🛠️ Instalacion y Ejecucion

1.  **Requisitos:**
    * Tener `python` instalado (version 3.6+ recomendada).
    * Tener la biblioteca `raylib-py`.

2.  **Instalar Raylib:**
    ```bash
    pip install raylib-py
    ```

3.  **Ejecutar el Juego:**
    Desde la carpeta raiz del proyecto (`ping_pong/`), ejecuta:
    ```bash
    python main.py
    ```

---

## 🎮 Como Jugar

### Objetivo

El objetivo es anotar **12 puntos** para ganar una ronda. El primer jugador en ganar **2 rondas** gana la partida.

### Controles

El juego soporta tanto teclado como mandos de Xbox (detectados automaticamente).

#### **Controles de Menu**

| Accion | Teclado | Mando Xbox |
| :--- | :--- | :--- |
| Moverse | Flechas Arriba/Abajo | Cruceta (D-pad) o Joystick Izquierdo (Arriba/Abajo) |
| Aceptar | `Enter` | Boton `(A)` |
| Atras / Pausa | `ESC` | Boton `(B)` o Boton `Start/Menu` |

#### **Controles en Partida (J1 - Izquierda)**

| Accion | Teclado | Mando Xbox |
| :--- | :--- | :--- |
| Moverse | `W` (Arriba) / `S` (Abajo) | Cruceta (D-pad) o Joystick Izquierdo (Analogico) |
| **Boost Normal**| Mantener `D` | Mantener `(A)` o `(X)` |
| **Super Boost (Dash)**| Tocar `A` | Tocar `(B)` o `(Y)` |

#### **Controles en Partida (J2 - Derecha)**

| Accion | Teclado | Mando Xbox |
| :--- | :--- | :--- |
| Moverse | `Flecha Arriba` / `Flecha Abajo` | Cruceta (D-pad) o Joystick Izquierdo (Analogico) |
| **Boost Normal**| Mantener `Flecha Izquierda`| Mantener `(A)` o `(X)` |
| **Super Boost (Dash)**| Tocar `Flecha Derecha` | Tocar `(B)` o `(Y)` |

---

### Mecanicas Especiales

#### Habilidades Especiales (Estamina)

Ambas habilidades consumen la misma barra de Estamina.

**Boost Normal (Mantener)**
* **Efecto:** Al mantener presionado, la velocidad de tu paleta se multiplica **x2.0**.
* **Visual:** La paleta de J1 se vuelve **Verde** y la de J2 **Roja**. Deja una estela.
* **Gasto:** Gasta la barra de estamina en **1.0 segundo** de uso continuo.

**Super Boost (Dash / Tocar)**
* **Efecto:** Es un sistema de **3 Cargas**. Cada toque gasta **33.3%** de la barra de estamina.
* **Movimiento:** Ejecuta un "dash" (o "blink") casi instantaneo (velocidad **x7.5** por 0.08 segundos).
* **Fisica:** Si golpeas la pelota *durante* el dash (o hasta 20 milisegundos despues de terminarlo), la pelota saldra disparada en un **angulo vertical totalmente aleatorio** y con mas velocidad.
* **Visual:** La paleta emite un **flash Amarillo** potente al activarse y deja una estela.

**Gestion de Estamina (General)**
* **Costo por Golpe:** Golpear la pelota (ya sea con Boost Normal o Super Boost) consume un **15%** de tu barra de estamina instantaneamente.
* **Recarga Normal:** Si dejas de usar estamina (y no la agotaste), la barra se recarga un **20% mas lento** de lo que se gasta (tarda 1.2 segundos en llenarse).
* **Penalizacion:** Si **agotas la estamina** (la barra se vacia), entras en un *cooldown* donde la barra se recarga un **50% mas lento** (tarda 1.5 segundos en llenarse).
* **Reset:** La estamina se restaura por completo al inicio de cada punto.

#### Tiempo Coyote

Para que el juego sea mas justo, tienes un bufer de **5 pixeles** por encima y por debajo de tu paleta. Si la bola golpea esta "zona fantasma", contara como un golpe valido.

**Importante:** Esta ayuda solo se activa si te estas moviendo activamente en el momento del impacto.