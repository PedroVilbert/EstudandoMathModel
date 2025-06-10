import dash
from matdata.dataset import *
from matmodel.util.parsers import df2trajectory
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

#Teste
# Carregando dados
ds = 'mat.FoursquareNYC'
df = load_ds(ds, sample_size=0.25)
T, data_desc = df2trajectory(df)
traj = T[0] #T[1] é uma pessoa especifica, caso mude o valor, muda a pessoa 

"""
    Os aspects são cada uma das colunas, no caso 
    1. space (space2d), 2. time (datetime), 3. day (nominal), 4. poi (nominal), 5. type (nominal), 
    6. root_type (nominal), 7. rating (numeric), 8. weather (nominal)
    
"""

def icone_avaliacao(av):
    
    #divide a nota em 2, pois as notas estão de 0 até 10, mas as estrelas vão de 0 até 5
    avaliacao = av/2
        
    #Faz o valor da avaliação que é um float menos o valor inteiro da avaliação, sobrando apenas os decimais.
    meia_estrela = avaliacao - int(avaliacao)
    if meia_estrela >= 0.5: #Se o decimal for maior ou igual a 0.5 ele considera como ⯪
        meia_estrela = "⯪"
    else: #Se não a estrela é vazia 
        meia_estrela = "☆"
            
    # 5 - avaliação resulta em um valot float, é convertido para inteiro para multiplicar pelo numero de estrelas
    estrala_cinza = int(5 - avaliacao)
        
    if avaliacao >= 1: #Converte o valor da nota para o numero de '★', ex: se a nota for 2, se transforma em '★★☆☆☆'
        avaliacao =  (int(avaliacao) * "★") + (meia_estrela) + (estrala_cinza * "☆")
    elif avaliacao == 0: #O Valor da avaliação é 0
        avaliacao = estrala_cinza * "☆"
    else: #Valor da nota é negativo, no caso não tem nota, então atribui o simbolo '-'
        avaliacao = "\t -" 
        
    return avaliacao #Retorna a avaliação


def icones_clima(clima): 
    #Dicionario convertendo os textos para icones
    clima_icones = {
        "Clouds": "☁️",
        "Clear": "☀️",
        "Rain": "🌧️",
        "Snow": "❄️",
        "Fog": "🌫️",
        "Unknown": "-"
    }
    
    #Busco o icone referente ao testo que esta em clima_ponto
    icone = clima_icones.get(clima)
    return icone

# Monta o dataframe a partir da trajetória
coordenadas = []
for point in traj.points:
    #Função para convereter o valor numerico em estrelas para a valiação 
    avaliacao = icone_avaliacao(point.aspects[6].value)
    #Cria a verção numérica da avaliação indo de 0 até 5
    if point.aspects[6].value > 0:
        num_avaliacao = str(point.aspects[6].value /2)
    else: 
        num_avaliacao = "-"
    
    #Função para converter o clima em icone    
    icone = icones_clima(point.aspects[7].value)
    
    #Adiciona no array as coordenadas com os vatributos
    coordenadas.append({
        "lat": point.aspects[0].x, # Latitude (eixo X)
        "lon": point.aspects[0].y, # Longitude (eixo Y) 
        "Nome Local": str(point.aspects[3]), # Nome da localização
        "Tipo": str(point.aspects[4]), # Tipo da localização
        "Classificação": str(point.aspects[5]), # Classificação da licalização 
        "Horário": str(point.aspects[1]), # Horario do checkin
        "Dia": str(point.aspects[2]), # Dia referente ao checkin
        "Clima": icone, #clima
        "Avaliação": avaliacao + "\t(" + num_avaliacao + ")", # Avaliações em formato de '★' ou '-' caso seja não tenha nota, além de colocar a avaliação em formato numérico
        "Ponto": point.seq,
    })

# Cria um DataFrame com as coordenadas
df_coords = pd.DataFrame(coordenadas)

# Dash app
app = Dash(__name__)

app.layout = html.Div([
    dcc.Checklist(
        id='filtros-hover',
         # Opoções que iram aparecer como caixa para serem marcadas no para, label é o nome na caixa e vule o que vai aparecer na tooltip
            options=[
                {'label': 'Latitute', 'value': 'lat'},
                {'label': 'Longitude','value': 'lon'},
                {'label': 'Nome Local', 'value': 'Nome Local'},
                {'label': 'Classificação', 'value': 'Classificação'},
                {'label': 'Horário', 'value': 'Horário'},
                {'label': 'Clima', 'value': 'Clima'},
                {'label': 'Avaliação', 'value': 'Avaliação'},
                {'label': 'Tipo', 'value': 'Tipo'},
                {'label': 'Dia', 'value': 'Dia'},
                {'label': 'Ponto', 'value': 'Ponto'},
            ],
        value=['Avaliação'],  # Opções padrão marcadas
        inline=True,    
    ),
    
    html.Button('Remover Todas', id='remover-button', n_clicks=1), #Botão para remover todas as opções 
    html.Button('Preencher   Todas', id='preencher-todos-button', n_clicks=0), #Botão para preencher todas as opções
    dcc.Graph(id='mapa', style={'height': '700px'}, config={'scrollZoom': True}), 
])



# CALLBACK 1 – Atualizar mapa com base no checklist
@app.callback(
    Output('mapa', 'figure'),
    Input('filtros-hover', 'value')
)
def update_map(colunas_selecionadas):
    # Plotar no mapa
    fig = px.scatter_mapbox(
        df_coords, # DataFrame das coordenadas
        lat="lat", # Latitude (eixo x)
        lon="lon", # Longitude (eixo y)
        hover_name="Nome Local",  # Nome da localização
        zoom=8, # Ajuste o zoom conforme necessário
        mapbox_style="open-street-map", # Estilo do mapa (pode ser "stamen-terrain", "carto-positron", etc.)
        title="Trajetória no Mapa (FoursquareNYC)" # Titulo do mapa
    )
    
    # Monta hovertemplate dinamicamente conforme o filtro do usuário
    linhas = [] 
    for value, label in enumerate(colunas_selecionadas):
        linhas.append(f"{label}: %{{customdata[{value}]}}")
    hovertemplate = "<br>".join(linhas) + "<extra></extra>" if linhas else "%{hovertext}<extra></extra>"
    
    # Atualiza o gráfico para usar o hovertemplate customizado
    fig.update_traces(
        hovertemplate=hovertemplate,
        customdata=df_coords[colunas_selecionadas].values if colunas_selecionadas else None,
        marker=dict(size=8, symbol='circle'),
        line=dict(width=2, color='black'),
        mode='lines+markers'
    )  
    
    #faz o mapa ocupar a tela toda 
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, autosize=True)
    

    
    return fig

# callback 2 atualizar a seleção de opções para aperecer no mapa
@app.callback(
    Output('filtros-hover', 'value'),
    [Input('remover-button', 'n_clicks'), Input('preencher-todos-button', 'n_clicks')],
)
def atualizar_checklist(n_clicks1, n_clicks2):
    ctx = dash.callback_context #serve para entender qual botão chamoi o callback
    if ctx.triggered:
        botao_clicado = ctx.triggered[0]['prop_id'].split('.')[0]# Vai pegar o id do botão que foi clicado
        if botao_clicado == "remover-button":# Vai retornar a lista de seleção vazia
            return []
        elif botao_clicado == "preencher-todos-button":# Vai retornar a lista de seleção complelta
            return ['lat', 'lon', 'Nome Local', 'Classificação', 'Horário', 'Clima', 'Avaliação', 'Tipo', 'Dia', 'Ponto']       
    return []

if __name__ == "__main__":
    app.run(debug=True)
