from matdata.dataset import *
from matmodel.util.parsers import df2trajectory
import pandas as pd
from matmodel.base import Space2D
import plotly.express as px


ds = 'mat.FoursquareNYC'
df = load_ds(ds, sample_size=0.25)

T, data_desc = df2trajectory(df)
traj = T[0] #T[1] é uma pessoa especifica, caso mude o valor, muda a pessoa 

"""
    Os aspects são cada uma das colunas, no caso 
    1. space (space2d), 2. time (datetime), 3. day (nominal), 4. poi (nominal), 5. type (nominal), 
    6. root_type (nominal), 7. rating (numeric), 8. weather (nominal)
    
"""
"""
print(data_desc.attributes) # Lista os atributos
for point in traj.points:
    print(point.seq)
# for i in traj.points: # Traj.points é as trajetorias que a pessoa do T[1] fez
#     #if i.aspects[5].value == 'Travel & Transport' and i.aspects[2].value == "Monday": # Tem que usar i.value para acessar o valor do aspect
#         print("\npoi",i.aspects) # .aspects[3] é os lugares por onde a pessoa passou

"""
def mapa():
    # Extrai coordenadas (assumindo que aspects[0].x = latitude e aspects[0].y = longitude)
    coordenadas = [] # array com as coodenadas e nome da localização
    
    
    for point in traj.points:
        

        #Função para convereter o valor numerico em estrelas para a valiação 
        avaliacao = notas_mapa(point.aspects[6].value) 
        
        #Adiciona no array as coordenadas com os vatributos
        coordenadas.append({
            "lat": point.aspects[0].x,   # Latitude (eixo X)
            "lon": point.aspects[0].y,  # Longitude (eixo Y) 
            "text": str(point.aspects[3]), # Nome da localização
            "time": str(point.aspects[1]), # Horario do checkin
            "weather": str(point.aspects[7]), #clima
            "rating": avaliacao,
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
        hover_data= ["time", "weather", "rating", "point"], #data, clima, nota e ordem dos pontos do checkin
        zoom=8,  # Ajuste o zoom conforme necessário
        title="Trajetória no Mapa (FoursquareNYC)", # Titulo do mapa
        mapbox_style="open-street-map",  # Estilo do mapa (pode ser "stamen-terrain", "carto-positron", etc.)
        height=700, #Tamanho do mapa
    )   
            
    # Conectar os pontos com linhas
    fig.update_traces(marker=dict(size=8, symbol= 'circle'), line=dict(width=2, color='black'),mode='lines+markers')
    fig.show()


def notas_mapa(nota):
    
        #divide a nota em 2, pois as notas estão de 0 até 10, mas as estrelas vão de 0 até 5
        avaliacao = nota/2
        
        if avaliacao > 0 and avaliacao < 1:#Converte a nota para 1 caso o valor esteja entre 1 e zero e depois transfora em *
            avaliacao = 1
            avaliacao *= "*"
        elif avaliacao < 0: #Valor da nota é negativo, no caso não tem nota, então atribui o simbolo '/'
            avaliacao = "\t -"
        else: #Converte o valor da nota para o numero de '*', ex: se a nota for 2, se transforma em '**'
            avaliacao =  "*" * int(avaliacao)
        
        return avaliacao #Retorna a avaliação

print(data_desc.attributes) # Lista os atributos
mapa()

