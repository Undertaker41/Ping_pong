# Proyecto: Ping Pong Avanzado

Este es un juego clásico de Ping Pong desarrollado en Python y Raylib, pero con mecánicas modernas, una IA desafiante, y soporte completo para multijugador local y mandos de Xbox.

## 🚀 Características Principales

* **Gráficos Fluidos:** Corre a 1366x768p y 90 FPS.
* **Modos de Juego:** Juega solo contra la IA o en multijugador local (J1 vs J2).
* **IA Desafiante:** Múltiples niveles de dificultad, incluyendo un modo "Extremo (Jaque Mate)" casi imbatible.
* **Habilidad Especial (Boost):** Una mecánica de "Boost" que duplica tu velocidad, gestionada por una barra de estamina.
* **Soporte Completo de Mando:** Detección automática de mandos de Xbox (o compatibles) para J1 y J2, con controles completos en el juego y menús.
* **Mecánicas de "Game Feel":**
    * **Tiempo Coyote:** Un pequeño búfer de 5 píxeles que te permite golpear la bola aunque no estés perfectamente alineado, *solo si te estás moviendo*.
    * **Velocidad Progresiva:** La bola aumenta su velocidad (multiplicador) cuanto más dura el punto.
* **Historial de Partidas:** El juego guarda automáticamente los resultados de las partidas en un archivo `historial.txt`.

---

## 🛠️ Instalación y Ejecución

1.  **Requisitos:**
    * Tener `python` instalado (versión 3.6+ recomendada).
    * Tener la biblioteca `raylib-py`.

2.  **Instalar Raylib:**
    ```bash
    pip install raylib-py
    ```
    pip install pygame

3.  **Ejecutar el Juego:**
    Desde la carpeta raíz del proyecto (`ping_pong/`), ejecuta:
    ```bash
    python main.py
    ```

---

## 🎮 Cómo Jugar

### Objetivo

El objetivo es anotar **12 puntos** para ganar una ronda. El primer jugador en ganar **2 rondas** gana la partida.

### Controles

El juego soporta tanto teclado como mandos de Xbox (detectados automáticamente).

#### **Controles de Menú**

| Acción | Teclado | Mando Xbox |
| :--- | :--- | :--- |
| Moverse | Flechas Arriba/Abajo | Cruceta (D-pad) o Joystick Izquierdo (Arriba/Abajo) |
| Aceptar | `Enter` | Botón `(A)` |
| Atrás / Pausa | `ESC` | Botón `(B)` o Botón `Start/Menu` |

#### **Controles en Partida (J1 - Izquierda)**

| Acción | Teclado | Mando Xbox |
| :--- | :--- | :--- |
| Moverse | `W` (Arriba) / `S` (Abajo) | Cruceta (D-pad) o Joystick Izquierdo (Arriba/Abajo) |
| **Boost** | Mantener `D` | Mantener `(A)`, `(B)`, `(X)` o `(Y)` |

#### **Controles en Partida (J2 - Derecha)**

| Acción | Teclado | Mando Xbox |
| :--- | :--- | :--- |
| Moverse | `Flecha Arriba` / `Flecha Abajo` | Cruceta (D-pad) o Joystick Izquierdo (Arriba/Abajo) |
| **Boost** | Mantener `Flecha Izquierda` | Mantener `(A)`, `(B)`, `(X)` o `(Y)` |

---

### Mecánicas Especiales

#### Habilidad Especial (Boost)

* **Efecto:** Al mantener presionado el botón de Boost, la velocidad de tu paleta se multiplica **x2.0**.
* **Visual:** La paleta de J1 se vuelve **Celeste** y la de J2 **Amarilla**.
* **Estamina:**
    * Tienes **1.5 segundos** de Boost.
    * Si sueltas el botón antes de agotarla, la estamina se regenera 1 a 1 (tarda lo mismo en recargarse que lo que usaste).
    * Si **agotas la estamina** (la barra se pone roja), entras en un *cooldown* de **2.8 segundos** durante el cual no puedes usarla.
* **Reset:** La estamina se restaura por completo al inicio de cada punto.

#### Tiempo Coyote

Para que el juego sea más justo, tienes un búfer de **5 píxeles** por encima y por debajo de tu paleta. Si la bola golpea esta "zona fantasma", contará como un golpe válido.

**Importante:** Esta ayuda solo se activa si te estás moviendo activamente en el momento del impacto.