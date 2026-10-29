```markdown
# Monitor de Bitacoras con Automatas Finitos - Casilleros Inteligentes IoT

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![JFLAP](https://img.shields.io/badge/JFLAP-7.1-orange.svg)](https://www.jflap.org/)
[![LaTeX](https://img.shields.io/badge/Overleaf-LaTeX-green.svg)](https://www.overleaf.com/)

Sistema de monitoreo para la deteccion de anomalias y validacion de secuencias de eventos en un entorno de casilleros inteligentes (Smart Lockers) con control de acceso IoT y aplicacion web, basado en la Teoria de Automatas y Lenguajes Formales.

## Descripcion del Proyecto

El sistema analiza bitacoras de eventos (logs) organizadas por sesiones de uso. Cada evento capturado por la aplicacion web (reservas) o por el hardware IoT (teclado matricial, sensores opticos y de puerta) se mapea a un simbolo de un alfabeto formal Sigma.

El monitor aplica un Automata Finito Determinista Minimo (AFD Minimo) equivalente a la union de varios Automatas Finitos No Deterministas (AFND), permitiendo detectar violaciones de seguridad en tiempo de ejecucion con complejidad O(n) por sesion.

## Estructura del Repositorio

```text
proyecto-monitor/
├── README.md
├── datos/
│   ├── generador.py         # Genera datasets sinteticos con semilla fija (seed=42)
│   ├── validacion.csv       # Dataset de 320 sesiones etiquetadas
│   ├── prueba.csv           # Dataset de 50 sesiones a ciegas (para prueba en vivo)
│   └── clave_prueba.csv     # Clave de respuestas de prueba.csv
├── automatas/
│   ├── patron_p1_iii.jff    # AFND para P1 (3 PINs incorrectos seguidos)
│   ├── patron_p2_asinr.jff  # AFND para P2 (Apertura sin reserva previa)
│   ├── patron_p3_oe.jff     # AFND para P3 (Cierre de casillero ocupado sin auth)
│   ├── afnd_unido_epsilon.jff # Union de patrones mediante transiciones epsilon
│   └── afd_minimo.jff       # AFD Minimo optimizado resultante
├── monitor/
│   ├── automata.py          # Clases AFND, AFD, Subconjuntos y Minimizacion
│   └── monitor.py           # Script principal de lectura, evaluacion y metricas
└── informe/
    ├── informe_casilleros_inteligentes.pdf  # Informe tecnico formato Anexo B
    └── Anexo_A_Registro.pdf                 # Ficha de registro propuesta
```

## Alfabeto y Patrones Monitoreados

### Diccionario de Eventos (Sigma)

* R: RESERVA (Reserva iniciada desde la app web)
* C: CODIGO_CORRECTO (Autenticacion PIN exitosa en la cerradura)
* I: CODIGO_INCORRECTO (Intento fallido de PIN)
* A: PUERTA_ABIERTA (Sensor detecta apertura fisica del locker)
* E: PUERTA_CERRADA (Sensor detecta cierre fisico del locker)
* O: OCUPADO (Sensor optico/presencia detecta objeto dentro)
* L: CONSULTA_ESTADO (Evento neutro/irrelevante - bucle en automata)

### Patrones Detectados

1. Patron P1 (L1): Intento de fuerza bruta en cerradura (III).
2. Patron P2 (L2): Apertura fisica sin reserva previa activa (A sin R).
3. Patron P3 (L3): Intento de deposito o cierre anomalo de casillero ocupado (OE sin C).

## Requisitos e Instalacion

### Prerrequisitos

* Python 3.10 o superior.
* JFLAP 7.1 (opcional, para visualizacion interactiva de los archivos .jff).

### Clonar el repositorio

```bash
git clone [https://github.com/tu-usuario/proyecto-monitor.git](https://github.com/tu-usuario/proyecto-monitor.git)
cd proyecto-monitor

```

## Instrucciones de Ejecucion

### 1. Generacion de Conjuntos de Datos (Reproducible)

Para regenerar los archivos CSV en la carpeta datos/ asegurando reproducibilidad exacta (seed=42):

```bash
python datos/generador.py

```

### 2. Ejecucion del Monitor de Bitacoras

Para ejecutar la simulacion del automata, procesar los eventos y calcular las metricas globales:

```bash
python monitor/monitor.py

```

## Resultados y Metricas de Rendimiento

El monitor fue evaluado sobre un conjunto de 320 sesiones balanceadas (18% anomalas, 12% casi anomalas y 70% normales):

| Metrica | Resultado |
| --- | --- |
| Verdaderos Positivos (VP) | 58 |
| Falsos Positivos (FP) | 0 |
| Falsos Negativos (FN) | 0 |
| Precision | 100.0% |
| Exhaustividad (Recall) | 100.0% |
| Aceleracion (Speedup) | ~4.1x mas rapido usando el AFD Minimo frente al AFND |

## Tecnologias Utilizadas

* Python 3: Procesamiento de datos y logica formal del motor de simulacion.
* JFLAP 7.1: Diseno, simulacion y conversion de automatas finitos.
* LaTeX / Overleaf: Redaccion del informe tecnico conforme al Anexo B.

## Autores y Roles

* Integrante 1: Responsable del Modelo Formal (AFND, AFD y Minimizacion).
* Integrante 2: Desarrollador del Monitor en Python.
* Integrante 3: Responsable de Datos, Pruebas y Reproducibilidad.
* Integrante 4: Documentador e Integrador Tecnico.

Universidad Nacional de Loja - Teoria de Automatas y Computabilidad Avanzada (2026-2027)

```

```