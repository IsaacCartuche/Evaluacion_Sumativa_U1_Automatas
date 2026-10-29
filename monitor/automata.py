from collections import defaultdict, deque

class AFND:
    def __init__(self, estados, alfabeto, transiciones, estado_inicial, estados_aceptacion):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transiciones = transiciones  # dict: (estado, simbolo) -> set(estados)
        self.estado_inicial = estado_inicial
        self.estados_aceptacion = estados_aceptacion

    def clausura_epsilon(self, estados_set):
        clausura = set(estados_set)
        pila = list(estados_set)
        while pila:
            estado = pila.pop()
            alcanzables = self.transiciones.get((estado, 'ε'), set())
            for prox in alcanzables:
                if prox not in clausura:
                    clausura.add(prox)
                    pila.append(prox)
        return clausura

    def mover(self, estados_set, simbolo):
        alcanzables = set()
        for e in estados_set:
            alcanzables.update(self.transiciones.get((e, simbolo), set()))
        return alcanzables

    def evaluar_cadena(self, cadena):
        actuales = self.clausura_epsilon({self.estado_inicial})
        for simbolo in cadena:
            actuales = self.clausura_epsilon(self.mover(actuales, simbolo))
        return bool(actuales & self.estados_aceptacion)


class AFD:
    def __init__(self, estados, alfabeto, transiciones, estado_inicial, estados_aceptacion):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transiciones = transiciones  # dict: (estado, simbolo) -> estado
        self.estado_inicial = estado_inicial
        self.estados_aceptacion = estados_aceptacion

    def evaluar_cadena(self, cadena):
        actual = self.estado_inicial
        for simbolo in cadena:
            if (actual, simbolo) in self.transiciones:
                actual = self.transiciones[(actual, simbolo)]
            else:
                return False  # Transición no definida / Pozo
        return actual in self.estados_aceptacion


def afnd_a_afd(afnd):
    """Algoritmo de Construcción de Subconjuntos (Elimina ε e integra AFND)."""
    ini_closure = frozenset(afnd.clausura_epsilon({afnd.estado_inicial}))
    
    estados_afd = {ini_closure}
    cola = deque([ini_closure])
    trans_afd = {}
    
    mapeo_nombres = {ini_closure: "q0"}
    cont = 1
    
    while cola:
        conj_actual = cola.popleft()
        nombre_actual = mapeo_nombres[conj_actual]
        
        for sim in afnd.alfabeto:
            if sim == 'ε':
                continue
            alcanzados = afnd.mover(conj_actual, sim)
            closure = frozenset(afnd.clausura_epsilon(alcanzados))
            
            if not closure:
                continue
                
            if closure not in mapeo_nombres:
                mapeo_nombres[closure] = f"q{cont}"
                cont += 1
                estados_afd.add(closure)
                cola.append(closure)
                
            trans_afd[(nombre_actual, sim)] = mapeo_nombres[closure]
            
    estados_finales_afd = set()
    for conj, nombre in mapeo_nombres.items():
        if conj & afnd.estados_aceptacion:
            estados_finales_afd.add(nombre)
            
    return AFD(
        estados=set(mapeo_nombres.values()),
        alfabeto=[a for a in afnd.alfabeto if a != 'ε'],
        transiciones=trans_afd,
        estado_inicial="q0",
        estados_aceptacion=estados_finales_afd
    )

def minimizar_afd(afd):
    """Algoritmo de Minimización de AFD (Partición de equivalencias)."""
    F = set(afd.estados_aceptacion)
    no_F = set(afd.estados) - F
    
    particion = [F, no_F] if no_F else [F]
    
    cambio = True
    while cambio:
        cambio = False
        nueva_particion = []
        for grupo in particion:
            if len(grupo) <= 1:
                nueva_particion.append(grupo)
                continue
            
            subgrupos = defaultdict(set)
            for estado in grupo:
                clave = []
                for sim in afd.alfabeto:
                    destino = afd.transiciones.get((estado, sim), None)
                    idx_dest = -1
                    for idx, g in enumerate(particion):
                        if destino in g:
                            idx_dest = idx
                            break
                    clave.append(idx_dest)
                subgrupos[tuple(clave)].add(estado)
            
            nuevos_sub = list(subgrupos.values())
            nueva_particion.extend(nuevos_sub)
            if len(nuevos_sub) > 1:
                cambio = True
        particion = nueva_particion

    # Mapear estados equivalentes
    rep_map = {}
    nuevos_estados = set()
    estados_aceptacion_min = set()
    
    for idx, grupo in enumerate(particion):
        nombre = f"q_m{idx}"
        nuevos_estados.add(nombre)
        for e in grupo:
            rep_map[e] = nombre
            if e in afd.estados_aceptacion:
                estados_aceptacion_min.add(nombre)
                
    trans_min = {}
    for (orig, sim), dest in afd.transiciones.items():
        trans_min[(rep_map[orig], sim)] = rep_map[dest]
        
    return AFD(
        estados=nuevos_estados,
        alfabeto=afd.alfabeto,
        transiciones=trans_min,
        estado_inicial=rep_map[afd.estado_inicial],
        estados_aceptacion=estados_aceptacion_min
    )