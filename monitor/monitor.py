from collections import defaultdict
import csv
import os
import time
from automata import AFND, afnd_a_afd, minimizar_afd

# Rutas dinámicas
DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
DIR_RAIZ = os.path.abspath(os.path.join(DIR_ACTUAL, '..'))
DIR_DATOS = os.path.join(DIR_RAIZ, 'datos')


def resolver_ruta_csv(nombre_o_ruta):
  """Resuelve la ruta completa del CSV ya sea relativa a la raíz o a datos/."""
  if os.path.exists(nombre_o_ruta):
    return nombre_o_ruta

  ruta_en_datos = os.path.join(DIR_DATOS, nombre_o_ruta)
  if os.path.exists(ruta_en_datos):
    return ruta_en_datos

  raise FileNotFoundError(
      f"No se encontró el archivo '{nombre_o_ruta}' ni en la raíz ni en"
      f' {DIR_DATOS}'
  )


def construir_afnd_monitor():
  estados = {f'q{i}' for i in range(12)}
  alfabeto = {'R', 'C', 'I', 'A', 'E', 'O', 'L'}
  transiciones = defaultdict(set)

  transiciones[('q0', 'L')].add('q0')
  transiciones[('q0', 'R')].add('q0')
  transiciones[('q0', 'C')].add('q0')
  transiciones[('q0', 'E')].add('q0')
  transiciones[('q0', 'O')].add('q0')

  # P1: III
  transiciones[('q0', 'I')].add('q1')
  transiciones[('q1', 'I')].add('q2')
  transiciones[('q2', 'I')].add('q3')
  for sim in alfabeto:
    transiciones[('q3', sim)].add('q3')

  # P2: A sin R
  transiciones[('q0', 'A')].add('q6')
  for sim in alfabeto:
    transiciones[('q6', sim)].add('q6')

  # P3: OE
  transiciones[('q0', 'O')].add('q8')
  transiciones[('q8', 'E')].add('q9')
  for sim in alfabeto:
    transiciones[('q9', sim)].add('q9')

  return AFND(
      estados=estados,
      alfabeto=alfabeto,
      transiciones=transiciones,
      estado_inicial='q0',
      estados_aceptacion={'q3', 'q6', 'q9'},
  )


def procesar_csv(filepath):
  sesiones = defaultdict(list)
  etiquetas_reales = {}

  ruta_final = resolver_ruta_csv(filepath)

  with open(ruta_final, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
      s_id = row['id_sesion']
      sesiones[s_id].append(row['simbolo'])
      if 'etiqueta' in row:
        etiquetas_reales[s_id] = row['etiqueta']

  cadenas = {s_id: ''.join(sims) for s_id, sims in sesiones.items()}
  return cadenas, etiquetas_reales


def ejecutar_evaluacion(csv_path='validacion.csv', clave_path=None):
  cadenas, etiquetas = procesar_csv(csv_path)

  if clave_path:
    ruta_clave = resolver_ruta_csv(clave_path)
    with open(ruta_clave, 'r', encoding='utf-8') as f:
      reader = csv.DictReader(f)
      etiquetas = {row['id_sesion']: row['etiqueta'] for row in reader}

  afnd = construir_afnd_monitor()
  afd = afnd_a_afd(afnd)
  afd_min = minimizar_afd(afd)

  print('=' * 60)
  print(' MONITOREO DE BITÁCORAS - CASILLEROS INTELIGENTES')
  print('=' * 60)
  print(f'Archivo analizado         : {csv_path}')
  print(f'Total de sesiones         : {len(cadenas)}')
  print(
      f'Estados AFND              : {len(afnd.estados)} | Transiciones:'
      f' {sum(len(v) for v in afnd.transiciones.values())}'
  )
  print(
      f'Estados AFD Mínimo        : {len(afd_min.estados)} | Transiciones:'
      f' {len(afd_min.transiciones)}'
  )
  print('-' * 60)

  t0_afnd = time.perf_counter()
  for s_id, cad in cadenas.items():
    afnd.evaluar_cadena(cad)
  t_afnd = (time.perf_counter() - t0_afnd) * 1000

  t0_afd = time.perf_counter()
  predicciones = {}
  for s_id, cad in cadenas.items():
    es_anomala = afd_min.evaluar_cadena(cad)
    predicciones[s_id] = 'anómala' if es_anomala else 'normal'
  t_afd = (time.perf_counter() - t0_afd) * 1000

  if etiquetas:
    vp, fp, fn, vn = 0, 0, 0, 0
    for s_id, pred in predicciones.items():
      real = etiquetas[s_id]
      if real == 'anómala' and pred == 'anómala':
        vp += 1
      elif real == 'normal' and pred == 'anómala':
        fp += 1
      elif real == 'anómala' and pred == 'normal':
        fn += 1
      else:
        vn += 1

    precision = vp / (vp + fp) if (vp + fp) > 0 else 0.0
    exhaustividad = vp / (vp + fn) if (vp + fn) > 0 else 0.0

    print(f'Verdaderos Positivos (VP) : {vp}')
    print(f'Falsos Positivos (FP)     : {fp}')
    print(f'Falsos Negativos (FN)     : {fn}')
    print(f'Verdaderos Negativos (VN) : {vn}')
    print(f'Precisión                : {precision:.4f} ({precision*100:.2f}%)')
    print(
        'Exhaustividad (Recall)  :'
        f' {exhaustividad:.4f} ({exhaustividad*100:.2f}%)'
    )
    print('-' * 60)

  print(f'Tiempo de ejecución AFND   : {t_afnd:.4f} ms')
  print(f'Tiempo de ejecución AFD Min : {t_afd:.4f} ms')
  if t_afd > 0:
    print(f'Aceleración (Speedup)      : {t_afnd/t_afd:.2f}x más rápido el AFD')
  print('=' * 60)


if __name__ == '__main__':
  ejecutar_evaluacion('validacion.csv')