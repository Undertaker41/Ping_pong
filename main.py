# main.py (Version Funcional)
"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
descripcion: Archivo principal de ejecucion (Version Funcional).
Inicia el Modelo, la Vista y el Controlador y corre el bucle
principal del juego. No usa Clases.
"""
try:
    import raylibpy as rl
except ImportError:
    print("Error: No se pudo importar la biblioteca 'raylibpy'.")
    print("Por favor, instálela usando: pip install raylib-py")
    exit()

# Importamos los modulos que ahora contienen solo funciones
import modelo
import vista
import controlador

def main():
    """
    Funcion principal que inicializa y corre el juego.
    """
    
    # 1. Inicializar los componentes
    
    # Creamos el diccionario que contendra TODO el estado del juego
    estado_juego = modelo.crear_estado_inicial()
    
    # Inicializamos la ventana de Raylib y los colores de la vista
    vista.inicializar_vista()
    
    # El controlador ya no necesita ser inicializado, es solo un modulo de funciones.

    # 2. Bucle principal del juego
    
    # El bucle ahora comprueba el flag 'debe_cerrar' DENTRO del diccionario de estado
    while not rl.window_should_close() and not estado_juego['debe_cerrar']:
   
        # 3. Obtener el tiempo delta
        delta_tiempo = rl.get_frame_time()
        
        # 4. Procesar Entradas (Controlador)
        # El controlador lee los inputs y retorna un objeto 'Entradas' (un diccionario)
        # Tambien puede modificar el 'estado_juego' (ej. para el 'axis_neutral')
        entradas = controlador.procesar_entradas(estado_juego)
        
        # 5. Actualizar Estado (Modelo)
        # ESTA ES LA CLAVE DEL ENFOQUE FUNCIONAL:
        # La funcion de logica toma el estado actual y las entradas...
        # ...y retorna un NUEVO estado actualizado.
        estado_juego = modelo.actualizar_estado(estado_juego, entradas, delta_tiempo)
        
        # 6. Dibujar (Vista)
        # La vista toma el estado actualizado y dibuja la pantalla.
        vista.dibujar(estado_juego)

    # 7. Limpiar al salir
    vista.cerrar_vista()
    
    
    print("\n¡Gracias por jugar!\n")
  

if __name__ == "__main__":
    main()