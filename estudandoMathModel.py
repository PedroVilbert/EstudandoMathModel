from matdata.dataset import *
from matmodel.util.parsers import df2trajectory
import pandas as pd
from matmodel.base import Space2D
import plotly.express as px
from PIL import Image


ds = 'mat.FoursquareNYC'
df = load_ds(ds, sample_size=0.25)

T, data_desc = df2trajectory(df)
traj = T[0] #T[1] é uma pessoa especifica, caso mude o valor, muda a pessoa 

"""
    Os aspects são cada uma das colunas, no caso 
    1. space (space2d), 2. time (datetime), 3. day (nominal), 4. poi (nominal), 5. type (nominal), 
    6. root_type (nominal), 7. rating (numeric), 8. weather (nominal)
    
"""

def mapa():
    # Extrai coordenadas (assumindo que aspects[0].x = latitude e aspects[0].y = longitude)
    coordenadas = [] # array com as coodenadas e nome da localização
    
    
    for point in traj.points:
        

        #Função para convereter o valor numerico em estrelas para a valiação 
        avaliacao = avaliacoes(point.aspects[6].value) 

        #Função para converter o clima em icone
        icone = icones_clima(point.aspects[7].value)
        
        #Adiciona no array as coordenadas com os vatributos
        coordenadas.append({
            "lat": point.aspects[0].x,   # Latitude (eixo X)
            "lon": point.aspects[0].y,  # Longitude (eixo Y) 
            "text": str(point.aspects[3]), # Nome da localização
            "type": str(point.aspects[4]),  # Tipo da localização
            "root_type": str(point.aspects[5]), # Classificação da licalização 
            "time": str(point.aspects[1]), # Horario do checkin
            "day": str(point.aspects[2]), # Dia referente ao checkin
            "weather": icone, #clima
            "rating": avaliacao, # Avaliações em formato de '*' ou '-' caso seja não tenha nota 
            "point": point.seq,
        })

    # Cria um DataFrame com as coordenadas
    df_coords = pd.DataFrame(coordenadas)

    # Plotar no mapa
    fig = px.scatter_mapbox(
        df_coords, # DataFrame das coordenadas
        lat="lat", # Latitude (eixo x)
        lon="lon",# Longitude (eixo y)
        hover_name= "text", # Nome da localização
        hover_data= ["time", "day", "type", "root_type", "weather", "rating", "point"], #data, clima, nota e ordem dos pontos do checkin
        zoom=8,  # Ajuste o zoom conforme necessário
        title="Trajetória no Mapa (FoursquareNYC)", # Titulo do mapa
        mapbox_style="open-street-map",  # Estilo do mapa (pode ser "stamen-terrain", "carto-positron", etc.)
        height=700, #Tamanho do mapa
    )   
    
    #Habilita o zoom pelo mouse
    config = {'scrollZoom': True} 
    
    #faz o mapa ocupar a tela toda 
    fig.update_layout(
        margin={"r":0,"t":30,"l":0,"b":0},  # Remove margens
        autosize=True)
    
    # Conectar os pontos com linhas
    fig.update_traces(marker=dict(size=8, symbol= 'circle'),
                      line=dict(width=2, color='black'),
                      mode='lines+markers')
    fig.show(config = config)

def avaliacoes(av):
    
        #divide a nota em 2, pois as notas estão de 0 até 10, mas as estrelas vão de 0 até 5
        avaliacao = av/2
        
        #Se o resto da divisão for diferente de zero, então considera como meia estrela
        meia_estrela = "" #Começa como vazio para caso a divisão tenha um resultado vazio
        if av%2 != 0:
            meia_estrela = "⯪"
            
        #5 - o numero inteiro da avaliação será a quantidade de estrelas cinzas
        estrala_cinza = int(5 - avaliacao)
        
        if avaliacao > 0 and avaliacao < 1:#Converte a nota para 1 caso o valor esteja entre 1 e zero e depois transfora em *
            avaliacao = 1
            avaliacao = (avaliacao * "⯪") + (estrala_cinza * "☆")
        elif avaliacao < 0: #Valor da nota é negativo, no caso não tem nota, então atribui o simbolo '/'
            avaliacao = "\t -"
        elif avaliacao > 1: #Converte o valor da nota para o numero de '*', ex: se a nota for 2, se transforma em '**'
            avaliacao =  (int(avaliacao) * "★") + (meia_estrela) + (estrala_cinza * "☆")
        else:
            avaliacao = estrala_cinza * "☆"  
        
        return avaliacao #Retorna a avaliação


def icones_clima(clima): 
    #Dicionario convertendo os textos para icones
    clima_icones = {
        "Clouds": "☁️",
        "Clear": "☀️",
        "Rain": "🌧️",
        "Snow": "❄️",
        "Fog": "🌫️"
    }
    
    #Busco o icone referente ao testo que esta em clima_ponto
    icone = clima_icones.get(clima)
    return icone
      
        
print(data_desc.attributes) # Lista os atributos

mapa()

#Teste
# for point in traj.points:
#     print(point.aspects[4].value, point.aspects[5])

