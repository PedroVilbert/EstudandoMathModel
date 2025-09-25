import dash  # Importa a biblioteca Dash para criação da aplicação web interativa
from matdata.dataset import *  # Importa funções para carregar datasets do pacote matdata
from matmodel.util.parsers import df2trajectory  # Importa função para converter DataFrame em trajetórias
import plotly.graph_objects as go  # Importa plotly.graph_objects para gráficos customizados
from dash import Dash, dcc, html, Input, Output  # Importa componentes do Dash para construir layout e callbacks
from matdata.dataset import load_ds
from matdata.converter import df2csv
from matdata.preprocess import klabels_stratify
from matmodel.util.parsers import json2movelet
import json
import pandas as pd
import os

# Carregando dados das trajetorias
ds = 'mat.FoursquareNYC'  # Define o nome do dataset a ser carregado
df = load_ds(ds, sample_size=0.25)  # Carrega uma amostra de 25% do dataset
T, data_desc = df2trajectory(df)  # Converte DataFrame em múltiplas trajetórias (lista T)



# Carregando dados das movelets----------------------------------------------------------------------------------
dataset='mat.FoursquareNYC'

data = load_ds(dataset, missing='-999')
print(data)
#-------------------------------------------------------------------
train, test = klabels_stratify(data, kl=10)

print("Classes:", train.label.unique())

print("Trajs. Treino:", len(train.tid.unique()) )
print("Trajs. Teste :", len(test.tid.unique()) )


#-------------------------------------------------------------------
data_path = 'sample/data/FoursquareNYC'
if not os.path.exists(data_path):
    os.makedirs(data_path)

df2csv(train, data_path, 'train')
df2csv(test, data_path, 'test')


#--------------------------------------------------------------------
prog_path = 'sample/programs'
if not os.path.exists(prog_path):
    print(os.makedirs(prog_path))

# Criar pastas se não existirem
os.makedirs("sample/programs", exist_ok=True)
os.makedirs("sample/data/FoursquareNYC", exist_ok=True)

# Baixar o JAR
url_jar = "https://raw.githubusercontent.com/mat-analysis/mat-tools/main/jarfiles/MoveletDiscovery.jar"
jar_path = "sample/programs/MoveletDiscovery.jar"
r = requests.get(url_jar)
with open(jar_path, "wb") as f:
    f.write(r.content)
print("MoveletDiscovery.jar baixado!")

# Baixar o JSON
url_json = "https://raw.githubusercontent.com/mat-analysis/datasets/main/mat/FoursquareNYC/FoursquareNYC.json"
json_path = "sample/data/FoursquareNYC/FoursquareNYC.json"
r = requests.get(url_json)
with open(json_path, "wb") as f:
    f.write(r.content)
print("FoursquareNYC.json baixado!")
    
#--------------------------------------------------------------------

import subprocess

cmd = [
    "java", "-Xmx7G", "-jar", "./sample/programs/MoveletDiscovery.jar",
    "-curpath", "./sample/data/FoursquareNYC",
    "-respath", "./sample/results/hiper",
    "-descfile", "./sample/data/FoursquareNYC/FoursquareNYC.json",
    "-nt", "1", "-version", "hiper", "-ms", "-1", "-Ms", "-3", "-TC", "1d"
]

subprocess.run(cmd, check=True)

#--------------------------------------------------------------------


movelets_train = pd.read_csv('./sample/data/FoursquareNYC/train.csv')
movelets_test = pd.read_csv('./sample/data/FoursquareNYC/test.csv')

#--------------------------------------------------------------------

T, data_desc = df2trajectory(data, data_desc='sample/data/FoursquareNYC/FoursquareNYC.json')

#--------------------------------------------------------------------
# Lendo movelets como objetos de mat-model

mov_file = './sample/results/hiper/Movelets/HIPER_Log_FoursquareNYC_LSP_ED/164/moveletsOnTrain.json'

with open(mov_file, 'r') as f:
    M = json2movelet(f)
    
    
    
# Cria dicionário de trajetórias com movelets
traj_movelets = {}
for mov in M:  # M é a lista de movelets extraídas pelo json2movelet
    tid = mov.tid  # ID da trajetória da qual movelet foi extraída
    if tid not in traj_movelets:
        traj_movelets[tid] = []
    traj_movelets[tid].append(mov)
print("Dicionario criado!")

# print("Total de trajetórias:", len(T))  # Código comentado para imprimir o total de trajetórias
# for i in range(5):  # Código comentado para mostrar número de pontos nas primeiras 5 trajetórias
#     print(f"Trajetória {i+1} contém {len(T[i].points)} pontos")

# Definição de funções auxiliares
def icone_avaliacao(av):  # Função para converter valor numérico de avaliação em estrelas
    avaliacao = av / 2  # Divide avaliação por 2 para escalar de 0 a 5
    meia_estrela = "⯪" if (avaliacao - int(avaliacao)) >= 0.5 else "☆"  # Decide se meia estrela deve aparecer
    estrela_cinza = int(5 - avaliacao)  # Quantidade de estrelas cinzas para completar até 5

    if avaliacao >= 1:  # Se avaliação >= 1, monta string com estrelas cheias, meia e cinzas
        return (int(avaliacao) * "★") + meia_estrela + (estrela_cinza * "☆")
    elif avaliacao == 0:  # Se avaliação 0, retorna só estrelas cinzas
        return estrela_cinza * "☆"
    else:  # Caso contrário, retorna símbolo de ausência de avaliação
        return "\t -"

def icones_clima(clima):  # Função para converter string clima em emoji correspondente
    clima_icones = {
        "Clouds": "☁️",  # Nuvens
        "Clear": "☀️",   # Sol
        "Rain": "🌧️",    # Chuva
        "Snow": "❄️",    # Neve
        "Fog": "🌫️",     # Névoa
        "Unknown": "-"   # Desconhecido
    }
    return clima_icones.get(clima, '-')  # Retorna emoji ou '-' se não encontrado

# Inicia app
app = Dash(__name__)  # Instancia aplicação Dash

# Layout
app.layout = html.Div([  # Define layout principal como uma Div
    dcc.Checklist(  # Checklist para seleção das colunas a mostrar no tooltip
        id='filtros-hover',  # Id do componente para callbacks
        options=[  # Opções que aparecem como checkboxes
            {'label': 'Latitute', 'value': 'lat'},  # Latitude
            {'label': 'Longitude','value': 'lon'},  # Longitude
            {'label': 'Nome Local', 'value': 'Nome Local'},  # Nome do local
            {'label': 'Classificação', 'value': 'Classificacao'},  # Classificação do local
            {'label': 'Horário', 'value': 'Horario'},  # Horário do check-in
            {'label': 'Clima', 'value': 'Clima'},  # Clima no check-in
            {'label': 'Avaliação', 'value': 'Avaliacao'},  # Avaliação do local
            {'label': 'Tipo', 'value': 'Tipo'},  # Tipo do local
            {'label': 'Dia', 'value': 'Dia'},  # Dia do check-in
            {'label': 'Ponto', 'value': 'Ponto'},  # Número sequencial do ponto
        ],
        value=['Avaliacao', 'Clima'],  # Opções pré-selecionadas no checklist
        inline=True,  # Mostra as opções em linha
    ),
    html.Button('Remover Todas', id='remover-button', n_clicks=0),  # Botão para desmarcar todas opções (inicia clicado)
    html.Button('Preencher Todas', id='preencher-todos-button', n_clicks=1),  # Botão para marcar todas opções
    dcc.Graph(id='mapa', style={'height': '700px'}, config={'scrollZoom': True})  # Componente gráfico para mostrar o mapa
])

def extrair_valor(coluna, p):  # Função que retorna o valor de uma coluna para um ponto p da trajetória
    
    #Cria a versão numérica da avaliação indo de 0 até 5
    if p.aspects[6].value > 0:  # Se valor da avaliação for maior que zero
        num_avaliacao = str(p.aspects[6].value / 2)  # Divide por 2 e converte para string
    else: 
        num_avaliacao = "-"  # Caso contrário, retorna '-'
    
    # Dicionário que associa coluna ao valor extraído do ponto p
    idx = {
        "lat": lambda p: p.aspects[0].x,  # Latitude (coordenada x)
        "lon": lambda p: p.aspects[0].y,  # Longitude (coordenada y)
        "Nome Local": lambda p: str(p.aspects[3]),  # Nome do local (aspecto 3)
        "Classificacao": lambda p: str(p.aspects[5]),  # Classificação do local (aspecto 5)
        "Horario": lambda p: str(p.aspects[1]),  # Horário do check-in (aspecto 1)
        "Clima": lambda p: icones_clima(p.aspects[7].value),  # Clima formatado (aspecto 7)
        "Avaliacao": lambda p: icone_avaliacao(p.aspects[6].value) + "\t(" + num_avaliacao + ")",  # Avaliação com estrelas + número
        "Tipo": lambda p: str(p.aspects[4]),  # Tipo do local (aspecto 4)
        "Dia": lambda p: str(p.aspects[2]),  # Dia do check-in (aspecto 2)
        "Ponto": lambda p: p.seq  # Número sequencial do ponto
    }
    return idx[coluna](p) if coluna in idx else ''  # Retorna valor da coluna ou string vazia se coluna não existir

# CALLBACK 1 – Atualiza o mapa com múltiplas trajetórias
@app.callback(
    Output('mapa', 'figure'),  # Saída do callback atualiza a figura do gráfico do mapa
    Input('filtros-hover', 'value')  # Entrada é a lista das colunas selecionadas no checklist
)
def update_map(colunas_selecionadas):  # Função que atualiza o mapa com base nas colunas selecionadas
    fig = go.Figure()  # Cria uma nova figura plotly
    cores = ['blue', 'green', 'orange', 'purple', 'brown']  # Lista de cores para trajetórias

    all_lats = []  # Lista para armazenar todas latitudes dos pontos para centralizar mapa
    all_lons = []  # Lista para armazenar todas longitudes

    for i, traj in enumerate(T[:40]):  # Testando traj. desse intervalo para encontrar movelets
        lats = [p.aspects[0].x for p in traj.points]  # Lista de latitudes da trajetória i
        lons = [p.aspects[0].y for p in traj.points]  # Lista de longitudes da trajetória i
        all_lats.extend(lats)  # Adiciona latitudes à lista geral
        all_lons.extend(lons)  # Adiciona longitudes à lista geral

        print("O tid da trajetoria é: ", traj.tid)
        # Verifica se a trajetória possui algum movelet
        tem_movelet = traj.tid in traj_movelets
        print(tem_movelet, "-------------------------------------------------------------------------------------")
        # Cor normal da trajetória (não muda mais)
        cor_traj = cores[i % len(cores)]

        hover_texts = []  # Lista que conterá o texto do tooltip para cada ponto
        for j, p in enumerate(traj.points):  # Para cada ponto na trajetória
            titulo = f"{p.aspects[3].value}"  # Nome do local (aspecto 3)
            partes = [f"{c}: {extrair_valor(c, p)}" for c in colunas_selecionadas]  # Monta linhas com colunas selecionadas

            # Se a trajetória tem movelet, deixa TODO o texto em negrito
            if tem_movelet:
                texto = "<b>" + "<br>".join([titulo] + partes + ["🚩 MOVELET"]) + "</b>"
            else:
                texto = "<br>".join([titulo] + partes)

            hover_texts.append(texto)

        # Linha da trajetória
        fig.add_trace(go.Scattermapbox(
            mode='lines',
            lon=lons,
            lat=lats,
            line={'width': 2, 'color': cor_traj},  # Sempre cor normal
            name=f'Trajetória {i+1}',
            legendgroup=f"traj{i}",
            showlegend=True
        ))

        # Pontos da trajetória
        fig.add_trace(go.Scattermapbox(
            mode='markers',
            lon=lons,
            lat=lats,
            marker={'size': 8, 'color': cor_traj},  # Sempre cor normal
            name=f'Pontos T{i+1}',
            customdata=[[text] for text in hover_texts],  # Tooltip customizado
            hovertemplate="%{customdata[0]}<extra></extra>",
            legendgroup=f"traj{i}",
            showlegend=False
        ))

    # Centraliza o mapa
    if all_lats and all_lons:
        center_lat = sum(all_lats) / len(all_lats)
        center_lon = sum(all_lons) / len(all_lons)
    else:
        center_lat, center_lon = 0, 0

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=11,
        mapbox_center={"lat": center_lat, "lon": center_lon},
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        height=700,
        title="Múltiplas Trajetórias no Mapa",
        showlegend=True
    )

    return fig

# CALLBACK 2 – Atualiza checklist
@app.callback(
    Output('filtros-hover', 'value'),  # Saída atualiza valores selecionados no checklist
    [Input('remover-button', 'n_clicks'), Input('preencher-todos-button', 'n_clicks')]  # Entradas: cliques nos botões
)
def atualizar_checklist(n_clicks1, n_clicks2):  # Função que atualiza checklist com base no botão clicado
    ctx = dash.callback_context  # Contexto do callback para saber qual input disparou
    if ctx.triggered:  # Se algum input disparou callback
        botao = ctx.triggered[0]['prop_id'].split('.')[0]  # Captura id do botão disparador
        if botao == 'remover-button':  # Se botão "Remover Todas" foi clicado
            return []  # Retorna lista vazia para desmarcar todas as opções
        elif botao == 'preencher-todos-button':  # Se botão "Preencher Todas" foi clicado
            return ['lat', 'lon', 'Nome Local', 'Classificacao', 'Horario', 'Clima', 'Avaliacao', 'Tipo', 'Dia', 'Ponto']  # Retorna lista completa para marcar todas as opções
    raise dash.exceptions.PreventUpdate  # Se nenhum botão válido disparou, não atualiza nada

if __name__ == '__main__':  # Só executa quando rodar o script diretamente
    app.run(debug=True)  # Roda o servidor do Dash em modo debug para desenvolvimento

