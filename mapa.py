from io import StringIO
import dash  # Importa a biblioteca Dash para criação da aplicação web interativa
import plotly.graph_objects as go  # Importa plotly.graph_objects para gráficos customizados
from dash import Dash, dcc, html, Input, Output, State  # Importa componentes do Dash para construir layout e callbacks
import os
from dash import dcc

#bibliotecas mat
from matdata.dataset import *  # Importa funções para carregar datasets do pacote matdata
from matmodel.util.parsers import df2trajectory  # Importa função para converter DataFrame em trajetórias
from matdata.dataset import load_ds

#outros arquivos 
import funcoesAuxiliares as fca #Funções auxiliares para o mapa
import uploadArquivo as upa #Funções para o upload de arquivos
import movelets as mov #Movelets

# os.system('cls')
# import inspect
# print(inspect.getsource(df2trajectory))

# Carregando dados das trajetorias
ds = 'mat.FoursquareNYC'  # Define o nome do dataset a ser carregado
df = load_ds(ds, sample_size=0.25)  # Carrega uma amostra de 25% do dataset
T, data_desc = df2trajectory(df)  # Converte DataFrame em múltiplas trajetórias (lista T)

#-----------------------------------
# Inicia app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #Estilo para o botão
app = Dash(__name__, external_stylesheets=external_stylesheets)  # Instancia aplicação Dash

# Layout
app.layout = html.Div([  # Define layout principal como uma Div
    
    dcc.Dropdown(  # Checklist para seleção das colunas a mostrar no tooltip
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
        multi=True, # permite multiplas opções
        closeOnSelect=False,
        searchable=True
    ),
    html.Button('Remover Todas', id='remover-button', n_clicks=0),  # Botão para desmarcar todas opções (inicia clicado)
    html.Button('Preencher Todas', id='preencher-todos-button', n_clicks=0),  # Botão para marcar todas opções
    
    dcc.Upload(
    id='upload-data',
    children=html.Button('Upload File'),
    multiple=False
    ), #Botão de upload
    html.Div(id='upload-output'),  # Aqui aparecerá o resultado (mensagem de sucesso/erro)
    dcc.Store(id='store-data', storage_type='memory'),

 
    dcc.Graph(id='mapa', style={'height': '700px'}, config={'scrollZoom': True}), # Componente gráfico para mostrar o mapa
])



#-------------------------------------------------------------------------
# CALLBACK 1 – Atualiza o mapa com múltiplas trajetórias
@app.callback(
    Output('mapa', 'figure'),
    Input('filtros-hover', 'value'),
    Input('store-data', 'data')  # Novo input
)
def update_map(colunas_selecionadas, json_data):  # Função que atualiza o mapa com base nas colunas selecionadas
    
    global T  # Permite substituir as trajetórias globais
    
    # Se houver novos dados carregados, converte de volta para DataFrame e trajetórias
    if json_data is not None:
        df = pd.read_json(StringIO(json_data), orient='split')
        df = pd.read_json(StringIO(json_data), orient='split')

        T, data_desc = df2trajectory(
            df,
            data_desc=None,               # evita leitura de arquivo
            tid_col='tid',                # ajuste para o nome da sua coluna
            label_col='label'             # ajuste para sua coluna
        )
    
    fig = go.Figure()  # Cria uma nova figura plotly
    cores = ['blue', 'green', 'orange', 'purple', 'brown']  # Lista de cores para trajetórias

    all_lats = []  # Lista para armazenar todas latitudes dos pontos para centralizar mapa
    all_lons = []  # Lista para armazenar todas longitudes

    for i, traj in enumerate(T[:5]):  # Testando traj. desse intervalo para encontrar movelets
        lats = [p.aspects[0].x for p in traj.points]  # Lista de latitudes da trajetória i
        lons = [p.aspects[0].y for p in traj.points]  # Lista de longitudes da trajetória i
        all_lats.extend(lats)  # Adiciona latitudes à lista geral
        all_lons.extend(lons)  # Adiciona longitudes à lista geral

        # Ainda não sei se esta funcionando corretamente...
        # Verifica se a trajetória possui algum movelet
        tem_movelet = traj.tid in mov.traj_movelets.keys()

        # Cor normal da trajetória (não muda mais)
        cor_traj = cores[i % len(cores)]

        hover_texts = []  # Lista que conterá o texto do tooltip para cada ponto
        for j, p in enumerate(traj.points):  # Para cada ponto na trajetória
            titulo = f"{p.aspects[3].value}"  # Nome do local (aspecto 3)
            partes = [f"{c}: {fca.extrair_valor(c, p)}" for c in colunas_selecionadas]  # Monta linhas com colunas selecionadas

            # Se a trajetória tem movelet, deixa todo o texto em negrito
            if tem_movelet:
                texto = "<b>" + "<br>".join([titulo] + partes + ["🚩 MOVELET"]) + "</b>"
                print("🚩 MOVELET")
            else:
                texto = "<br>".join([titulo] + partes)

            hover_texts.append(texto)

        # Linha da trajetória
        fig.add_trace(go.Scattermap(
            mode='lines',
            lon=lons,
            lat=lats,
            line={'width': 2, 'color': cor_traj},  # Sempre cor normal
            name=f'Trajetória {i+1}',
            legendgroup=f"traj{i}",
            showlegend=True
        ))

        # Pontos da trajetória
        fig.add_trace(go.Scattermap(
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
        map_style="open-street-map",
        map_zoom=11,
        map_center={"lat": center_lat, "lon": center_lon},
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



@app.callback(
    Output('store-data', 'data'),  # Salva o DataFrame no Store
    Output('upload-output', 'children'),  # Mostra mensagem
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'),
    prevent_initial_call=True
)
def process_uploaded_file(contents, filename, date):
    if contents is not None:
        df = upa.parse_contents(contents, filename, date)

        if isinstance(df, pd.DataFrame):

            #CONVERSÕES AQUI DENTRO!!!
            # Converte colunas com caracteres estranhos
            df['day'] = df['day'].astype(str).str.replace(r'[^a-zA-ZÀ-ÖØ-öø-ÿ\s]', '', regex=True).str.strip()
            df['poi'] = df['poi'].astype(str).str.replace(r'[^a-zA-ZÀ-ÖØ-öø-ÿ\s&]', '', regex=True).str.strip()
            df['type'] = df['type'].astype(str).str.replace(r'[^a-zA-ZÀ-ÖØ-öø-ÿ\s&]', '', regex=True).str.strip()
            df['root_type'] = df['root_type'].astype(str).str.replace(r'[^a-zA-ZÀ-ÖØ-öø-ÿ\s&]', '', regex=True).str.strip()
            df['weather'] = df['weather'].astype(str).str.replace(r'[^a-zA-ZÀ-ÖØ-öø-ÿ\s]', '', regex=True).str.strip()

            # Normaliza linhas vazias
            df = df.replace({"": None, "nan": None})

            return df.to_json(date_format='iso', orient='split'), f"✅ Arquivo {filename} carregado com sucesso!"

        else:
            return None, f"⚠️ Erro ao processar o arquivo: {df}"

    return None, ''

    
if __name__ == '__main__':  # Só executa quando rodar o script diretamente
    app.run(debug=True)  # Roda o servidor do Dash em modo debug para desenvolvimento
    
    
    