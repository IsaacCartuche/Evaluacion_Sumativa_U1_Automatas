import csv
import random
from datetime import datetime, timedelta

# Configuración de reproducibilidad
random.seed(42)

# Diccionario de Eventos (Alfabeto Sigma)
EVENTOS = {
    'R': ('RESERVA', 'Reserva realizada desde la app web', True),
    'C': ('CODIGO_CORRECTO', 'Código PIN correcto ingresado en el locker', True),
    'I': ('CODIGO_INCORRECTO', 'Código PIN incorrecto ingresado', True),
    'A': ('PUERTA_ABIERTA', 'Sensor detecta apertura del locker', True),
    'E': ('PUERTA_CERRADA', 'Sensor detecta cierre del locker', True),
    'O': ('OCUPADO', 'Sensor óptico/presencia detecta objeto dentro', True),
    'L': ('CONSULTA_ESTADO', 'Consulta de estado o encendido LED', False) # Irrelevante
}

SIMBOLOS = list(EVENTOS.keys())

def generar_sesion_normal(id_sesion):
    """Genera un flujo normal válido: R -> C -> A -> O -> E -> L"""
    eventos = ['R', 'L', 'C', 'A', 'O', 'E', 'L']
    # Insertar eventos irrelevantes aleatorios
    if random.random() < 0.4:
        eventos.insert(random.randint(0, len(eventos)), 'L')
    return eventos, 'normal', 'NINGUNO'

def generar_sesion_casi_anomala(id_sesion):
    """Sesión casi anómala (ej: 2 intentos fallidos II en vez de 3 III)"""
    # CASI P1: Dos intentos incorrectos, luego acierta
    eventos = ['R', 'I', 'I', 'C', 'A', 'O', 'E']
    if random.random() < 0.3:
        eventos.append('L')
    return eventos, 'normal', 'NINGUNO'

def generar_sesion_anomala_p1(id_sesion):
    """P1: Tres códigos incorrectos seguidos III"""
    prefix = ['R'] if random.random() < 0.5 else []
    eventos = prefix + ['I', 'I', 'I', 'L']
    return eventos, 'anómala', 'P1'

def generar_sesion_anomala_p2(id_sesion):
    """P2: Apertura A sin reserva previa R"""
    eventos = ['I', 'A', 'O', 'E']
    if random.random() < 0.5:
        eventos.insert(0, 'L')
    return eventos, 'anómala', 'P2'

def generar_sesion_anomala_p3(id_sesion):
    """P3: Cierre E de casillero ocupado O sin código correcto previa en secuencia OE"""
    eventos = ['R', 'A', 'O', 'E'] # Falta el código correcto C
    return eventos, 'anómala', 'P3'

def crear_dataset(filename_csv, num_sesiones=320, incluir_etiquetas=True, filename_clave=None):
    base_time = datetime(2026, 10, 20, 8, 0, 0)
    filas = []
    clave_filas = []
    
    id_evento_global = 1000
    
    for i in range(1, num_sesiones + 1):
        id_sesion = f"S-{i:04d}"
        actor_id = f"USR-{random.randint(100, 999)}"
        
        # Proporción: ~18% anómalas, 12% casi anómalas, 70% normales
        r = random.random()
        if r < 0.06:
            evs, etq, patron = generar_sesion_anomala_p1(id_sesion)
        elif r < 0.12:
            evs, etq, patron = generar_sesion_anomala_p2(id_sesion)
        elif r < 0.18:
            evs, etq, patron = generar_sesion_anomala_p3(id_sesion)
        elif r < 0.30:
            evs, etq, patron = generar_sesion_casi_anomala(id_sesion)
        else:
            evs, etq, patron = generar_sesion_normal(id_sesion)
            
        clave_filas.append({'id_sesion': id_sesion, 'etiqueta': etq, 'tipo_patron': patron})
        
        for sim in evs:
            nombre_ev, desc, rel = EVENTOS[sim]
            base_time += timedelta(seconds=random.randint(2, 15))
            
            fila = {
                'id_evento': id_evento_global,
                'fecha_hora': base_time.strftime('%Y-%m-%d %H:%M:%S'),
                'id_sesion': id_sesion,
                'actor': actor_id,
                'evento': nombre_ev,
                'simbolo': sim
            }
            if incluir_etiquetas:
                fila['etiqueta'] = etq
                fila['tipo_patron'] = patron
                
            filas.append(fila)
            id_evento_global += 1

    # Guardar CSV principal
    fieldnames = list(filas[0].keys())
    with open(filename_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filas)
        
    # Si hay clave separada (para prueba.csv)
    if filename_clave:
        with open(filename_clave, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id_sesion', 'etiqueta', 'tipo_patron'])
            writer.writeheader()
            writer.writerows(clave_filas)

if __name__ == '__main__':
    print("Generando archivo de validación (320 sesiones con etiquetas)...")
    crear_dataset('validacion.csv', num_sesiones=320, incluir_etiquetas=True)
    
    print("Generando archivo de prueba (50 sesiones sin etiquetas)...")
    crear_dataset('prueba.csv', num_sesiones=50, incluir_etiquetas=False, filename_clave='clave_prueba.csv')
    print("Datasets generados exitosamente con semilla reproducible (seed=42).")