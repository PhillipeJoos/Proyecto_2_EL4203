import tkinter as tk
from tkinter import messagebox
import numpy as np

# --- Importamos tu lógica ---
# Asegúrate de que tu archivo original se llame 'connect4_logic.py'
from main import Tablero, Jugador, FILAS, COLUMNAS, VACIO, JUGADOR_HUMANO, JUGADOR_IA, JUGADOR_RANDOM

# --- Configuración Visual ---
TAMANO_CELDA = 80
RADIO = 30
COLOR_FONDO = "#0055D4"    # Azul clásico de Connect 4
COLOR_VACIO = "#FFFFFF"    # Blanco
COLOR_J1 = "#FF3333"       # Rojo
COLOR_J2 = "#FFFF33"       # Amarillo

class Connect4GUI:
    def __init__(self, root, jugador1_type=JUGADOR_HUMANO, jugador2_type=JUGADOR_IA):
        self.root = root
        self.root.title("Connect 4 - IA Project")

        # 1. Inicializar la lógica del juego (Backend)
        self.jugador1 = Jugador(jugador1_type, "X")
        self.jugador2 = Jugador(jugador2_type, "O")

        self.tablero = Tablero()
        self.turno_actual = self.jugador1 # Empieza jugador 1
        self.game_over = False

        # 2. Elementos de la Interfaz
        self.canvas = tk.Canvas(
            root, 
            width=COLUMNAS * TAMANO_CELDA, 
            height=FILAS * TAMANO_CELDA, 
            bg=COLOR_FONDO
        )
        self.canvas.pack()

        # Label para mostrar mensajes
        self.info_label = tk.Label(root, text=f"Turn: {self.turno_actual.ficha}", font=("Arial", 14))
        self.info_label.pack(pady=10)

        # Botón de reinicio
        self.btn_reset = tk.Button(root, text="Reiniciar Juego", command=self.reset_game)
        self.btn_reset.pack(pady=5)

        self.btn_main_menu = tk.Button(root, text="Main Menu", command=self.main_menu)
        self.btn_main_menu.pack(pady=5)

        # 3. Bindings (Eventos)
        self.canvas.bind("<Button-1>", self.manejar_clic)

        # 4. Dibujar el estado inicial
        self.dibujar_tablero()

    def dibujar_tablero(self):
        """Dibuja la grilla y las fichas basándose en self.tablero.grid"""
        self.canvas.delete("all") # Limpiar canvas
        
        # Iterar sobre la matriz (grid) de tu clase Tablero
        # Nota: Tu grid usa filas 0 abajo, pero Tkinter dibuja 0 arriba.
        # Hacemos un flip visual o iteramos invertido. Tu método imprimir usa np.flip.
        # Aquí dibujaremos directo: fila 0 de numpy es fila 0 de tkinter (arriba)
        # PERO en tu lógica fila 0 suele ser abajo. Ajustemos visualmente:
        
        grid_visual = np.flip(self.tablero.grid, axis=0) 

        for r in range(FILAS):
            for c in range(COLUMNAS):
                x0 = c * TAMANO_CELDA
                y0 = r * TAMANO_CELDA
                x1 = x0 + TAMANO_CELDA
                y1 = y0 + TAMANO_CELDA
                
                # Dibujar recuadro azul
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=COLOR_FONDO, outline="")

                # Determinar color de la ficha
                valor = grid_visual[r][c]
                if valor == VACIO:
                    color = COLOR_VACIO
                elif valor == self.jugador1.ficha:
                    color = COLOR_J1
                else:
                    color = COLOR_J2

                # Dibujar circulo
                self.canvas.create_oval(
                    x0 + (TAMANO_CELDA//2) - RADIO,
                    y0 + (TAMANO_CELDA//2) - RADIO,
                    x0 + (TAMANO_CELDA//2) + RADIO,
                    y0 + (TAMANO_CELDA//2) + RADIO,
                    fill=color, outline="black"
                )
        self.root.update() # Forzar actualización visual

    def manejar_clic(self, event):
        """Maneja el turno del Humano basado en dónde hizo clic."""
        if self.game_over:
            return

        # Si es turno de la IA, ignoramos clics humanos
        if self.turno_actual.tipo_jugador != JUGADOR_HUMANO:
            return

        # Calcular columna basada en la coordenada X del clic
        col = event.x // TAMANO_CELDA

        if 0 <= col < COLUMNAS and self.tablero.es_columna_valida(col):
            self.ejecutar_jugada(col)
        else:
            print("Columna llena o inválida")

    def ejecutar_jugada(self, col):
        """Inserta ficha, actualiza GUI, verifica victoria y cambia turno."""
        
        # 1. Insertar en lógica
        fila = self.tablero.insertar_ficha(col, self.turno_actual.ficha)
        
        # 2. Actualizar visual
        self.dibujar_tablero()

        # 3. Verificar Victoria
        if self.tablero.detectar_victoria(self.turno_actual.ficha, fila, col):
            self.info_label.config(text=f"¡Ganó {self.turno_actual.ficha}!")
            messagebox.showinfo("Fin del juego", f"¡El jugador {self.turno_actual.ficha} ha ganado!")
            self.game_over = True
            return

        # 4. Verificar Empate
        if self.tablero.esta_lleno():
            self.info_label.config(text="¡Empate!")
            messagebox.showinfo("Fin del juego", "¡Es un empate!")
            self.game_over = True
            return

        # 5. Cambiar Turno
        if self.turno_actual == self.jugador1:
            self.turno_actual = self.jugador2
        else:
            self.turno_actual = self.jugador1
        
        self.info_label.config(text=f"Turno: {self.turno_actual.ficha} ({self.turno_actual.tipo_jugador})")

        # 6. Si el siguiente es IA/Random, ejecutar su turno automáticamente
        if self.turno_actual.tipo_jugador in [JUGADOR_IA, JUGADOR_RANDOM]:
            # Usamos .after() para dar un pequeño retraso y que se note que "piensa"
            # y para no congelar la interfaz
            self.root.after(500, self.turno_ia)

    def turno_ia(self):
        """Ejecuta la lógica de la IA."""
        if self.game_over: 
            return
            
        # Llamamos a tu método elegir_columna (que tendrá el Minimax o Random)
        col = self.turno_actual.elegir_columna(self.tablero)
        
        if col is not None and self.tablero.es_columna_valida(col):
            self.ejecutar_jugada(col)
        else:
            # Caso de error raro si la IA elige columna llena
            print("Error: IA eligió columna inválida")

    def reset_game(self):
        """Reinicia el tablero y variables."""
        self.tablero = Tablero()
        self.turno_actual = self.jugador1
        self.game_over = False
        self.info_label.config(text=f"Turno: {self.turno_actual.ficha}")
        self.dibujar_tablero()

    def main_menu(self):
        """Regresa al menú principal."""
        self.root.destroy()
        main_menu = tk.Tk()
        MainMenu(main_menu)
        main_menu.mainloop()

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 - Menú Principal")

        self.frame_principal = tk.Frame(root)
        self.frame_principal.pack(pady=20)

        self.label = tk.Label(self.frame_principal, text="Selecciona el tipo de jugadores", font=("Arial", 16))
        self.label.pack(pady=10)

        self.btn_human_vs_ai = tk.Button(self.frame_principal, text="Humano vs Humano", command=lambda: self.iniciar_partida(JUGADOR_HUMANO, JUGADOR_HUMANO))
        self.btn_human_vs_ai.pack(pady=5)

        self.btn_ai_vs_random = tk.Button(self.frame_principal, text="Humano vs IA", command=lambda: self.iniciar_partida(JUGADOR_HUMANO, JUGADOR_IA))
        self.btn_ai_vs_random.pack(pady=5)

        self.btn_human_vs_random = tk.Button(self.frame_principal, text="IA vs Random", command=lambda: self.iniciar_partida(JUGADOR_IA, JUGADOR_RANDOM))
        self.btn_human_vs_random.pack(pady=5)

        self.btn_ai_vs_human = tk.Button(self.frame_principal, text="IA vs IA", command=lambda: self.iniciar_partida(JUGADOR_IA, JUGADOR_IA))
        self.btn_ai_vs_human.pack(pady=5)

    def iniciar_partida(self, j1, j2):
        self.root.destroy()  # Cerrar menú principal
        juego = Connect4GUI(tk.Tk(), j1, j2)
        juego.root.mainloop()


# --- Main Loop ---
if __name__ == "__main__":
    root = tk.Tk()
    gui = MainMenu(root)
    root.mainloop()