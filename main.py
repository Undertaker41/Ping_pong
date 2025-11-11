"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez,Hector Vargas
-
Archivo principal (main) del proyecto.
Se encarga de iniciar el programa.
"""
# ==================== IMPORT
# Importa el módulo controlador, que contiene la lógica principal del menú
import controlador

# ==================== FUNCIONES
def main():
    """
    Función principal que inicia la aplicación.
    Llama al manejador del menú TUI en el controlador.
    """
    controlador.mostrar_tui()

# ==================== MAIN
# Este bloque asegura que el código dentro de él solo se ejecute
# cuando el script es corrido directamente (y no importado).
if __name__ == '__main__':
    try:
        # Inicia la función principal
        main()
    except KeyboardInterrupt:
        # Maneja la interrupción por Ctr+C de forma limpia
        print("\nPrograma interrumpido por el usuario.")
    except Exception as e:
        # Captura cualquier otro error inesperado
        print(f"Error inesperado: {e}")