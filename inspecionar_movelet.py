"""Script de inspeção de movelets.

Ao executar diretamente, carrega um exemplo de movelet em JSON e imprime atributos públicos e valores.
"""

import sys
from matmodel.util.parsers import json2movelet
import json

# Tenta carregar uma movelet para inspecionar sua estrutura
try:
    mov_file = './sample/results/hiper/Movelets/HIPER_Log_FoursquareNYC_LSP_ED/164/moveletsOnTrain.json'
    with open(mov_file, 'r') as f:
        M = json2movelet(f)
    
    if M:
        mov = M[0]  # Primeira movelet
        print('--- Atributos públicos da movelet ---')
        attrs = [attr for attr in dir(mov) if not attr.startswith('_')]
        for attr in attrs:
            print(f'  {attr}')
        
        print('\n--- Valores dos atributos ---')
        print(f'tid: {mov.tid}')
        
        # Tenta acessar atributos comuns
        for attr in ['start', 'end', 'startPoint', 'endPoint', 'points', 'p1', 'p2', 'trajectory']:
            if hasattr(mov, attr):
                val = getattr(mov, attr)
                print(f'{attr}: {val} (tipo: {type(val).__name__})')
        
        # Imprime toda a movelet para ver sua estrutura
        print(f'\nMovelet como string: {mov}')
        
except Exception as e:
    import traceback
    print(f'Erro: {e}')
    traceback.print_exc()
