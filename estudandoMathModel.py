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
'''
print(data_desc.attributes) # Lista os atributos
for i in traj.points: # Traj.points é as trajetorias que a pessoa do T[1] fez
    if i.aspects[5].value == 'Travel & Transport' and i.aspects[2].value == "Monday": # Tem que usar i.value para acessar o valor do aspect
        print("\nCordenada X: ",i.aspects[0].x, "\nCordeanda Y: ",i.aspects[0].y) # .aspects[3] é os lugares por onde a pessoa passou

'''
'''
def mapa1():
    coordenadasX = []
    coordenadasY = []
    print(data_desc.attributes) # Lista os atributos
    for i in traj.points: # Traj.points é as trajetorias que a pessoa do T[1] fez
        #Separando as cordenadas x e y 
        coordenadasX.append(i.aspects[0].x)
        coordenadasY.append(i.aspects[0].y)
    print(coordenadasX, "\n", coordenadasY)

    fig = px.line(
        x=coordenadasX, 
        y=coordenadasY,
        title="Trajetória",
        labels={'x': 'Coordenada X', 'y': 'Coordenada Y'}
    )
    fig.update_traces(mode='lines+markers')  # Mostra tanto linhas quanto pontos
    fig.show()

mapa1()

'''
def mapa2():
    # Extrai coordenadas (assumindo que aspects[0].x = longitude e aspects[0].y = latitude)
    coordenadas = []
    for point in traj.points:
        coordenadas.append({
            "lat": point.aspects[0].x,   # Longitude (eixo X)
            "lon": point.aspects[0].y,  # Latitude (eixo Y)
            "text": str(point.aspects[3]), # nome da localização
        })

    # Cria um DataFrame com as coordenadas
    df_coords = pd.DataFrame(coordenadas)

    # Plotar no mapa
    fig = px.scatter_mapbox(
        df_coords,
        lat="lat",
        lon="lon",
        hover_name= "text", 
        zoom=8,  # Ajuste o zoom conforme necessário
        title="Trajetória no Mapa (FoursquareNYC)", 
        mapbox_style="open-street-map",  # Estilo do mapa (pode ser "stamen-terrain", "carto-positron", etc.)
        height=700,
    )

    # Conectar os pontos com linhas
    fig.update_traces(marker=dict(size=8, symbol= 'circle'), line=dict(width=2, color='black'),mode='lines+markers')
    fig.show()
    

print(data_desc.attributes) # Lista os atributos
mapa2()
''''''