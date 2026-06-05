import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def calcular_delta_nota(impacto_val, saldo_val):
    """Calcula a variação da nota base do jogador."""
    impacto = ctrl.Antecedent(np.arange(0, 6, 1), 'impacto')
    saldo = ctrl.Antecedent(np.arange(-3, 4, 1), 'saldo')
    delta = ctrl.Consequent(np.arange(-1.0, 1.1, 0.1), 'delta')

    impacto.automf(names=['baixo', 'medio', 'alto'])
    saldo['negativo'] = fuzz.trimf(saldo.universe, [-3, -3, 0])
    saldo['neutro'] = fuzz.trimf(saldo.universe, [-1, 0, 1])
    saldo['positivo'] = fuzz.trimf(saldo.universe, [0, 3, 3])
    delta['cai_muito'] = fuzz.trimf(delta.universe, [-1.0, -1.0, -0.5])
    delta['mantem'] = fuzz.trimf(delta.universe, [-0.5, 0.0, 0.5])
    delta['sobe_muito'] = fuzz.trimf(delta.universe, [0.5, 1.0, 1.0])

    regras = [
        ctrl.Rule(impacto['alto'] & saldo['positivo'], delta['sobe_muito']),
        ctrl.Rule(impacto['alto'] & saldo['neutro'], delta['sobe_muito']),
        ctrl.Rule(impacto['alto'] & saldo['negativo'], delta['mantem']),
        ctrl.Rule(impacto['medio'] & saldo['positivo'], delta['sobe_muito']),
        ctrl.Rule(impacto['medio'] & saldo['neutro'], delta['mantem']),
        ctrl.Rule(impacto['medio'] & saldo['negativo'], delta['cai_muito']),
        ctrl.Rule(impacto['baixo'] & saldo['positivo'], delta['mantem']),
        ctrl.Rule(impacto['baixo'] & saldo['neutro'], delta['cai_muito']),
        ctrl.Rule(impacto['baixo'] & saldo['negativo'], delta['cai_muito'])
    ]
    
    sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras))
    sim.input['impacto'] = float(impacto_val)
    sim.input['saldo'] = float(saldo_val)
    
    try:
        sim.compute()
        return sim.output['delta']
    except:
        return 0.0

def calcular_bonus_sinergia(jogos, taxa):
    """Calcula bónus de entrosamento."""
    freq = ctrl.Antecedent(np.arange(0, 21, 1), 'freq')
    taxa_f = ctrl.Antecedent(np.arange(0, 101, 1), 'taxa')
    bonus = ctrl.Consequent(np.arange(0.0, 1.6, 0.1), 'bonus')

    freq['baixa'] = fuzz.trimf(freq.universe, [0, 0, 8])
    freq['media'] = fuzz.trimf(freq.universe, [4, 10, 16])
    freq['alta'] = fuzz.trimf(freq.universe, [12, 20, 20])
    
    taxa_f['baixa'] = fuzz.trimf(taxa_f.universe, [0, 0, 45])
    taxa_f['media'] = fuzz.trimf(taxa_f.universe, [35, 50, 65])
    taxa_f['alta'] = fuzz.trimf(taxa_f.universe, [55, 100, 100])
    
    bonus['nulo'] = fuzz.trimf(bonus.universe, [0.0, 0.0, 0.3])
    bonus['baixo'] = fuzz.trimf(bonus.universe, [0.1, 0.4, 0.7])
    bonus['medio'] = fuzz.trimf(bonus.universe, [0.5, 0.8, 1.1])
    bonus['alto'] = fuzz.trimf(bonus.universe, [0.9, 1.5, 1.5])

    regras = [
        ctrl.Rule(freq['alta'] & taxa_f['alta'], bonus['alto']),
        ctrl.Rule(freq['media'] & taxa_f['alta'], bonus['medio']),
        ctrl.Rule(freq['alta'] & taxa_f['media'], bonus['baixo']),
        ctrl.Rule(freq['baixa'] | taxa_f['baixa'], bonus['nulo'])
    ]
    
    sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras))
    sim.input['freq'] = float(jogos)
    sim.input['taxa'] = float(taxa)
    
    try:
        sim.compute()
        return sim.output['bonus']
    except:
        return 0.0