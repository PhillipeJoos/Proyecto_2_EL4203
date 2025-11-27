import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. DATOS ---
data_str = """(X)    46.083    38.254    53.367    45.9013333333333    7.55813762333905
(O)    77.799    73.27    77.263    76.1106666666667    2.47464428420195
(X)    0.456    0.211    0.34    0.335666666666667    0.122557469512606
(O)    0.443    0.468    0.277    0.396    0.103812330674154
(X)    49.847    48.91    61.574    53.4436666666667    7.0566445520044
(O)    40.69    50.649    50.769    47.3693333333333    5.78478351654868
(X)    0.434    0.514    0.489    0.479    0.0409267638593623
(O)    0.42    0.294    0.505    0.406333333333333    0.106161826158621
(X)    71.83    67.926    81.75    73.8353333333333    7.1268341732731
(O)    69.174    73.495    78.262    73.6436666666667    4.54582361441063
(X)    0.7    0.339    0.391    0.476666666666667    0.195152077450724
(O)    0.424    0.308    0.121    0.284333333333333    0.152880127332931
(X)    39.495    41.541    40.061    40.3656666666667    1.05647779594904
(O)    38.289    47.665    48.77    44.908    5.75878693823621
(X)    0.707    0.316    0.245    0.422666666666667    0.248785717703676
(O)    0.518    0.302    0.685    0.501666666666667    0.192021700162595
(X)    31.813    33.896    40.732    35.4803333333333    4.66580371783183
(O)    34.275    36.899    49.595    40.2563333333333    8.19325120653171
(X)    0.414    0.26    0.531    0.401666666666667    0.135920319795582
(O)    0.429    0.363    0.484    0.425333333333333    0.0605832760201471
(X)    16.741    6.31    11.268    11.4396666666667    5.21761845417364
(O)    12.488    11.085    12.423    11.9986666666667    0.791925712004183
(X)    0.431    0.412    0.449    0.430666666666667    0.0185022521151706
(O)    0.453    0.406    0.434    0.431    0.0236431808350738
(X)    15.585    5.87    10.319    10.5913333333333    4.86322221714506
(O)    6.325    7.019    2.028    5.124    2.70357559539215
(X)    0.105    0.365    0.469    0.313    0.187488666324127"""

lines = data_str.strip().split('\n')
xy_data = []

# Procesamos y extraemos MEDIA (índice 4) y STD (índice 5)
jugada_count = 1

# Usamos range con paso de 2 para ir pares. 
# Si el número de líneas es impar (como ahora, 27), el loop captura la última correctamente
for i in range(0, len(lines), 2):
    # Datos de X (línea i)
    parts_x = lines[i].split()
    mean_x = float(parts_x[4])
    std_x = float(parts_x[5])
    
    # Datos de O (línea i+1)
    # Verificamos si EXISTE la línea i+1
    if i + 1 < len(lines):
        parts_o = lines[i+1].split()
        mean_o = float(parts_o[4])
        std_o = float(parts_o[5])
    else:
        # Si es la última y no tiene par (O), ponemos NaN para que no grafique nada
        mean_o = np.nan
        std_o = np.nan

    xy_data.append({
        'Jugada': jugada_count,
        'Valor_X': mean_x,
        'Std_X': std_x,
        'Valor_O': mean_o,
        'Std_O': std_o
    })
    jugada_count += 1

df = pd.DataFrame(xy_data)

# --- 2. GRAFICACIÓN CON FONDO AZUL ---

bg_color = '#110061'
text_color = 'white'

fig, ax = plt.subplots(figsize=(12, 6))

fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

# Serie 'jugador1' (Rojo, Cuadrados) -> Corresponde a (X)
ax.errorbar(df['Jugada'], df['Valor_X'], yerr=df['Std_X'], 
            color='#ff3333',
            ecolor='#ff3333', 
            marker='s', linestyle='-', linewidth=2, markersize=8, 
            label='(X) jugador1', capsize=5)

# Serie 'jugador2' (Amarillo/Dorado, Rombos) -> Corresponde a (O)
# Matplotlib automáticamente ignora los valores NaN, cortando la línea donde no hay datos
ax.errorbar(df['Jugada'], df['Valor_O'], yerr=df['Std_O'], 
            color='#ffff00', 
            ecolor='#ffff00', 
            marker='d', linestyle='-', linewidth=2, markersize=8, 
            label='(O) jugador2', capsize=5)

# --- ESTÉTICA ---
ax.set_title('Tiempo en función de las jugadas', fontsize=14, color=text_color, fontweight='bold')
ax.set_xlabel('Jugadas', fontsize=12, color=text_color)
ax.set_ylabel('Tiempo [ms]', fontsize=12, color=text_color)

ax.tick_params(axis='x', colors=text_color)
ax.tick_params(axis='y', colors=text_color)
# Mostramos todos los ticks de las jugadas (del 1 al 14)
ax.set_xticks(df['Jugada'])

for spine in ax.spines.values():
    spine.set_edgecolor(text_color)

ax.grid(axis='y', linestyle='--', color='white', alpha=0.3)
ax.set_ylim(bottom=0)

# Leyenda
legend = ax.legend(loc='best', borderaxespad=0.)
frame = legend.get_frame()
frame.set_facecolor(bg_color)
frame.set_edgecolor(text_color)
for text in legend.get_texts():
    text.set_color(text_color)

plt.tight_layout()
plt.savefig('zigzag_blue_final_fixed.pdf', facecolor=bg_color)
plt.show()