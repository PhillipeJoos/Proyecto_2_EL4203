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
        self.root.config(bg="black")

        # 1. Inicializar la lógica
        self.jugador1 = Jugador(jugador1_type, "X")
        self.jugador2 = Jugador(jugador2_type, "O")
        self.tablero = Tablero()
        self.turno_actual = self.jugador1
        self.game_over = False

        # 2. Interfaz
        self.canvas = tk.Canvas(root, width=COLUMNAS * TAMANO_CELDA, height=FILAS * TAMANO_CELDA)
        self.canvas.pack()

        # Label inicial
        self.info_label = tk.Label(root, text="Iniciando...", font=("Arial", 14, "bold"), bg="black", fg="white")
        self.info_label.pack(pady=10)
        
        # Botones
        self.btn_reset = tk.Button(root, text="Reiniciar Juego", command=self.reset_game)
        self.btn_reset.pack(pady=5)
        self.btn_main_menu = tk.Button(root, text="Main Menu", command=self.main_menu)
        self.btn_main_menu.pack(pady=5)

        # 3. Eventos
        self.canvas.bind("<Button-1>", self.manejar_clic)
        
        # 4. Configuración inicial visual
        centrar_ventana(root)
        self.actualizar_etiqueta() # <--- Ponemos el color/texto correcto desde el inicio
        self.dibujar_tablero()

        # 5. Turno inicial
        if self.turno_actual.tipo_jugador in [JUGADOR_IA, JUGADOR_RANDOM]:
            self.root.after(500, self.turno_ia)

    def actualizar_etiqueta(self):
        """Gestiona el color y texto del turno."""
        if self.game_over: return

        if self.turno_actual.ficha == "X":
            self.info_label.config(text=f"Turno: Rojo ({self.turno_actual.tipo_jugador})", fg=COLOR_J1)
        else:
            self.info_label.config(text=f"Turno: Amarillo ({self.turno_actual.tipo_jugador})", fg=COLOR_J2)

    def dibujar_tablero(self):
        self.canvas.delete("all")
        grid_visual = np.flip(self.tablero.grid, axis=0)

        for r in range(FILAS):
            for c in range(COLUMNAS):
                x0 = c * TAMANO_CELDA
                y0 = r * TAMANO_CELDA
                x1 = x0 + TAMANO_CELDA
                y1 = y0 + TAMANO_CELDA
                
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=COLOR_FONDO, outline="")

                valor = grid_visual[r][c]
                if valor == VACIO:
                    color = COLOR_VACIO
                elif valor == self.jugador1.ficha:
                    color = COLOR_J1
                else:
                    color = COLOR_J2

                self.canvas.create_oval(
                    x0 + (TAMANO_CELDA//2) - RADIO, y0 + (TAMANO_CELDA//2) - RADIO,
                    x0 + (TAMANO_CELDA//2) + RADIO, y0 + (TAMANO_CELDA//2) + RADIO,
                    fill=color, outline="black"
                )
        self.root.update()

    def manejar_clic(self, event):
        if self.game_over or self.turno_actual.tipo_jugador != JUGADOR_HUMANO:
            return
        col = event.x // TAMANO_CELDA
        if 0 <= col < COLUMNAS and self.tablero.es_columna_valida(col):
            self.ejecutar_jugada(col)

    def ejecutar_jugada(self, col):
        fila = self.tablero.insertar_ficha(col, self.turno_actual.ficha)
        self.dibujar_tablero()

        # Verificar Victoria
        if self.tablero.detectar_victoria(self.turno_actual.ficha, fila, col):
            if self.turno_actual.ficha == "X":
                nombre_ganador = "Rojo"
                color_texto = COLOR_J1
            else:
                nombre_ganador = "Amarillo"
                color_texto = COLOR_J2

            # Actualizamos la etiqueta con el texto y el color del ganador
            self.info_label.config(text=f"¡Ganó {nombre_ganador} ({self.turno_actual.tipo_jugador})!", fg=color_texto)
            
            # Actualizamos el popup
            messagebox.showinfo("Fin del juego", f"¡El jugador {nombre_ganador} ({self.turno_actual.tipo_jugador}) ha ganado!")
            
            self.game_over = True
            return

        # Verificar Empate
        if self.tablero.esta_lleno():
            self.info_label.config(text="¡Empate!", fg="black")
            messagebox.showinfo("Fin", "¡Empate!")
            self.game_over = True
            return

        # Cambiar Turno
        self.turno_actual = self.jugador2 if self.turno_actual == self.jugador1 else self.jugador1
        
        self.actualizar_etiqueta() 

        if self.turno_actual.tipo_jugador in [JUGADOR_IA, JUGADOR_RANDOM]:
            self.root.after(500, self.turno_ia)

    def turno_ia(self):
        if self.game_over: return
        self.root.update_idletasks() # Asegurar UI fluida
        col = self.turno_actual.elegir_columna(self.tablero)
        if col is not None and self.tablero.es_columna_valida(col):
            self.ejecutar_jugada(col)

    def reset_game(self):
        self.tablero = Tablero()
        self.turno_actual = self.jugador1
        self.game_over = False
        
        self.actualizar_etiqueta()
        
        self.dibujar_tablero()
        if self.turno_actual.tipo_jugador in [JUGADOR_IA, JUGADOR_RANDOM]:
            self.root.after(1000, self.turno_ia)

    def main_menu(self):
        self.root.destroy()
        root = tk.Tk()
        MainMenu(root)
        root.mainloop()

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 - Menú Principal")

        self.frame_principal = tk.Frame(root)
        self.frame_principal.pack(pady=20)
        centrar_ventana(root, ancho=300, alto=250)

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

def centrar_ventana(root, ancho=None, alto=None):
    """Centra la ventana en la pantalla."""
    root.update_idletasks()

    if ancho is None:
        ancho = root.winfo_width()
    if alto is None:
        alto = root.winfo_height()

    # Obtener el ancho y alto de la pantalla del monitor
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calcular la posición x, y
    x = (screen_width // 2) - (ancho // 2)
    y = (screen_height // 2) - (alto // 2)

    # Establecer la geometría
    root.geometry(f"{ancho}x{alto}+{x}+{y}")


# --- Main Loop ---
if __name__ == "__main__":
    root = tk.Tk()
    gui = MainMenu(root)
    root.mainloop()