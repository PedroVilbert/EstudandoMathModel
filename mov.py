import pandas as pd
import os
import subprocess
from matdata.dataset import *  # Importa funções para carregar datasets do pacote matdata
from matmodel.util.parsers import df2trajectory  # Importa função para converter DataFrame em trajetórias
from matdata.dataset import load_ds
from matdata.converter import df2csv
from matdata.preprocess import klabels_stratify
from matmodel.util.parsers import json2movelet


# Carrega dados para as movelets
dataset='mat.FoursquareNYC'
data = load_ds(dataset, missing='-999')
train, test = klabels_stratify(data, kl=10)

data_path = 'sample/data/FoursquareNYC'
if not os.path.exists(data_path):
    os.makedirs(data_path)

df2csv(train, data_path, 'train')
df2csv(test, data_path, 'test')

prog_path = 'sample/programs'
if not os.path.exists(prog_path):
    print(os.makedirs(prog_path))

# Criar pastas se não existirem
os.makedirs("sample/programs", exist_ok=True)
os.makedirs("sample/data/FoursquareNYC", exist_ok=True)
    
cmd = [
    "java", "-Xmx7G", "-jar", "./sample/programs/MoveletDiscovery.jar",
    "-curpath", "./sample/data/FoursquareNYC",
    "-respath", "./sample/results/hiper",
    "-descfile", "./sample/data/FoursquareNYC/FoursquareNYC.json",
    "-nt", "1", "-version", "hiper", "-ms", "-1", "-Ms", "-3", "-TC", "1d"
]

subprocess.run(cmd, check=True)
movelets_train = pd.read_csv('./sample/data/FoursquareNYC/train.csv')
movelets_test = pd.read_csv('./sample/data/FoursquareNYC/test.csv')

T, data_desc = df2trajectory(data, data_desc='sample/data/FoursquareNYC/FoursquareNYC.json')

# Lendo movelets como objetos de mat-model
mov_file = './sample/results/hiper/Movelets/HIPER_Log_FoursquareNYC_LSP_ED/164/moveletsOnTrain.json'

with open(mov_file, 'r') as f:
    M = json2movelet(f)
       
# Cria dicionário de trajetórias com movelets
traj_movelets = {}
for mov in M:  # M é a lista de movelets extraídas pelo json2movelet
    tid = mov.tid  # ID da trajetória da qual movelet foi extraída
    if tid not in traj_movelets.keys():
        traj_movelets[tid] = []
    traj_movelets[tid].append(mov)
print("Dicionario criado!")

