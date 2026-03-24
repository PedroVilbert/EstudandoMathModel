from io import StringIO
import dash  # Importa a biblioteca Dash para criação da aplicação web interativa
import plotly.graph_objects as go  # Importa plotly.graph_objects para gráficos customizados
from dash import Dash, dcc, html, Input, Output, State  # Importa componentes do Dash para construir layout e callbacks
import os
from dash import dcc
import re

#bibliotecas mat
from matdata.dataset import *  # Importa funções para carregar datasets do pacote matdata
from matmodel.util.parsers import df2trajectory  # Importa função para converter DataFrame em trajetórias
from matdata.dataset import load_ds

#outros arquivos 
import funcoesAuxiliares as fca #Funções auxiliares para o mapa
import uploadArquivo as upa #Funções para o upload de arquivos
import mov #Módulo para carregar movelets

# os.system('cls')
# import inspect
# print(inspect.getsource(df2trajectory))

# Carregando dados das trajetorias
ds = 'mat.FoursquareNYC'  # Define o nome do dataset a ser carregado
df = load_ds(ds, sample_size=0.25)  # Carrega uma amostra de 25% do dataset
T, data_desc = df2trajectory(df)  # Converte DataFrame em múltiplas trajetórias (lista T)

# Carregando movelets disponíveis
traj_movelets = mov.carregar_movelets_disponveis()  # Carrega dicionário de movelets por trajetória

#-----------------------------------
# Inicia app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #Estilo para o botão
app = Dash(__name__, external_stylesheets=external_stylesheets)  # Instancia aplicação Dash

# Layout
app.layout = html.Div([  # Define layout principal como uma Div
    
    dcc.Dropdown(  # Checklist para seleção das colunas a mostrar no tooltip
        id='filtros-hover',  # Id do componente para callbacks
        options=[],
        value=[],  # Opções pré-selecionadas no checklist
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

    html.Div([
        
        html.Label("Intervalo de trajetórias:"),

        html.Div([
            dcc.Input(
                id="inicio-input",
                type="number",
                min=0,
                step=1,
                value=0,
                style={"width": "100px"}
            ),
            html.Span(" até "),
            dcc.Input(
                id="fim-input",
                type="number",
                min=0,
                step=1,
                value=10,
                style={"width": "100px"}
            ),
        ], style={"marginBottom": "5px"}),

        html.Div(id="info-limites-traj")

    ]),

 
    dcc.Graph(id='mapa', style={'height': '700px'}, config={'scrollZoom': True}), # Componente gráfico para mostrar o mapa
])



#-------------------------------------------------------------------------
# CALLBACK 1 – Atualiza o mapa com múltiplas trajetórias
@app.callback(
    Output('mapa', 'figure'),
    Input('filtros-hover', 'value'),
    Input('store-data', 'data'),  # Novo input
    Input('inicio-input', 'value'),
    Input('fim-input', 'value')    
)
def update_map(colunas_selecionadas, json_data, inicio, fim):  # Função que atualiza o mapa com base nas colunas selecionadas

    
    if not colunas_selecionadas:
        colunas_selecionadas = []

    # Se houve upload
    if json_data is not None:

        df_base = pd.read_json(StringIO(json_data), orient='split')
        
        # DEBUGZIN
        print("Colunas recebidas:", df_base.columns.tolist())

        print("Linhas logo após read_json:", len(df_base))

        print("Valores únicos da coluna space:")
        print(df_base["space"].head())

        print("Quantidade de NaN em space:", df_base["space"].isna().sum())


        # CASO 1 — já tem lat/lon
        if "lat" in df_base.columns and "lon" in df_base.columns:

            df_base["lat"] = pd.to_numeric(df_base["lat"], errors="coerce")
            df_base["lon"] = pd.to_numeric(df_base["lon"], errors="coerce")
            df_base = df_base.dropna(subset=["lat", "lon"])
            df_base["space"] = (
                df_base["lat"].astype(str) + " " +
                df_base["lon"].astype(str)
            )
        
        # CASO 2 — já tem LAT/LON
        elif "LAT" in df_base.columns and "LON" in df_base.columns:

            df_base["LAT"] = pd.to_numeric(df_base["LAT"], errors="coerce")
            df_base["LON"] = pd.to_numeric(df_base["LON"], errors="coerce")
            df_base = df_base.dropna(subset=["LAT", "LON"])
            df_base["space"] = (
                df_base["LAT"].astype(str) + " " +
                df_base["LON"].astype(str)
            )

        # CASO 3 — tem coluna space
        elif "space" in df_base.columns:

            df_base = df_base.dropna(subset=["space"]) # Remove linhas onde "space" é NaN, pois não tem como extrair coordenadas
            df_base["space"] = df_base["space"].astype(str) # Garante que "space" é string para aplicar regex

            # extrai todos os números (inclusive negativos e decimais)
            coords = df_base["space"].str.extract(r'(-?\d+\.?\d*)[^0-9\-]+(-?\d+\.?\d*)')

            if coords.isna().any().any(): # Se alguma linha não conseguiu extrair coordenadas, mostra aviso e retorna mapa vazio
                print("Falha ao extrair coordenadas") # DEBUG
                return go.Figure() # Retorna figura vazia

            # Converte para numérico, forçando erros a NaN, e depois remove linhas com NaN
            df_base["lon"] = pd.to_numeric(coords[0], errors="coerce")
            df_base["lat"] = pd.to_numeric(coords[1], errors="coerce")

            # Remove linhas onde não conseguiu extrair coordenadas válidas
            df_base = df_base.dropna(subset=["lat", "lon"])

            print("Linhas após tratamento:", len(df_base))

        else:
            return go.Figure()


        T_local, data_desc_local = df2trajectory(
            df_base,
            data_desc=None,
            tid_col='tid',
            label_col='label'
        )

    else:
        # sem upload -> usa dataset original
        T_local = T
        data_desc_local = data_desc
        
    fig = go.Figure() # Cria uma nova figura plotly
    cores = ['blue', 'green', 'orange', 'purple', 'brown']  # Lista de cores para trajetórias

    all_lats = []  # Lista para armazenar todas latitudes dos pontos para centralizar mapa
    all_lons = []  # Lista para armazenar todas longitudes
    
    print("Quantidade de trajetórias:", len(T_local))
    

    for i in range(inicio, fim):
        traj = T_local[i]
        
        if not traj.points:
            continue

        # Descobre qual índice é o aspecto espacial
        space_index = None
        for idx, asp in enumerate(traj.points[0].aspects):
            if hasattr(asp, "x") and hasattr(asp, "y"):
                space_index = idx
                break

        if space_index is None:
            continue  # não encontrou aspecto espacial

        lats = [p.aspects[space_index].x for p in traj.points]
        lons = [p.aspects[space_index].y for p in traj.points]
            
        all_lats.extend(lats)  # Adiciona latitudes à lista geral
        all_lons.extend(lons)  # Adiciona longitudes à lista geral

        # Verifica se a trajetória possui algum movelet e obtém informações
        movelets_info = traj_movelets.get(traj.tid, [])
        tem_movelet = len(movelets_info) > 0

        # Cor padrão da trajetória (mantém cor original, e highlight vermelho só para segmentos de movelet)
        cor_traj = cores[i % len(cores)]
        espessura = 2

        hover_texts = []  # Lista que conterá o texto do tooltip para cada ponto
        
        for j, p in enumerate(traj.points):  # Para cada ponto na trajetória
            
            # Nome do local (aspecto 3)
            try:
                titulo = f"{p.aspects[3].value}"
            except:
                titulo = "Local"

            # Monta linhas com colunas selecionadas
            partes = [
                f"{c}: {fca.extrair_valor(c, p, data_desc_local)}"
                for c in colunas_selecionadas
            ]

            # Se a trajetória tem movelet, adiciona flag visual
            if tem_movelet:
                num_movelets = len(traj_movelets[traj.tid])
                texto = "<br>".join([titulo] + partes + [f"🚩 MOVELET ({num_movelets} encontrada(s))"])
            else:
                texto = "<br>".join([titulo] + partes)

            hover_texts.append(texto)

        # Desenha a trajetória completa como base (sinaliza no nome se há movelet)
        label_traj = f"Trajetória {traj.tid}"
        if tem_movelet:
            label_traj += " 🚩"  # sinal visual de presence de movelet

        fig.add_trace(go.Scattermap(
            mode='lines',
            lon=lons,
            lat=lats,
            line={'width': espessura, 'color': cor_traj},
            name=label_traj,
            legendgroup=f"traj{i}",
            showlegend=True
        ))

        # Se houver movelets, desenha apenas o(s) trecho(s) de movelet em destaque vermelho
        if tem_movelet:
            for idx_mov, mov_info in enumerate(movelets_info):
                start = int(mov_info.get('start', 0))
                end = int(mov_info.get('end', -1))

                if start < 0 or end >= len(lats) or start >= len(lats):
                    continue

                seg_lats = lats[start:end + 1]
                seg_lons = lons[start:end + 1]

                fig.add_trace(go.Scattermap(
                    mode='lines',
                    lon=seg_lons,
                    lat=seg_lats,
                    line={'width': 6, 'color': 'red'},
                    name=f'Trajetória {traj.tid}',
                    legendgroup=f"traj{i}",
                    showlegend=False
                ))

        # Pontos da trajetória
        fig.add_trace(go.Scattermap(
            mode='markers',
            lon=lons,
            lat=lats,
            marker={'size': 8, 'color': cor_traj},
            name=f'Pontos T{i+1}',
            customdata=[[text] for text in hover_texts],
            hovertemplate="%{customdata[0]}<extra></extra>",
            legendgroup=f"traj{i}",
            showlegend=False
        ))

    print("Total latitudes coletadas:", len(all_lats))
    
    # Centraliza o mapa
    if all_lats and all_lons:
        center_lat = sum(all_lats) / len(all_lats)
        center_lon = sum(all_lons) / len(all_lons)
    else:
        center_lat, center_lon = 0, 0

    fig.update_layout(
        map_style="open-street-map",
        map_zoom=5,
        map_center={"lat": center_lat, "lon": center_lon},
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        height=700,
        title="Múltiplas Trajetórias no Mapa",
        showlegend=True
    )

    return fig

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

            # Padroniza nomes das colunas
            df.columns = df.columns.str.strip().str.lower()

            print("Colunas recebidas:", df.columns.tolist())

            # Converte colunas de texto automaticamente
            for col in df.select_dtypes(include=['object']).columns:
                if col == "space":
                    continue  # NÃO mexe na coluna space
                
                df[col] = df[col].astype(str).str.strip()

            # Tenta converter colunas numéricas automaticamente
            for col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col])
                except:
                    pass

            # Normaliza linhas vazias
            df = df.replace({"": None, "nan": None})

            return df.to_json(date_format='iso', orient='split'), f"✅ Arquivo {filename} carregado com sucesso!"

        else:
            return None, f"⚠️ Erro ao processar o arquivo: {df}"

    return None, ''


#callback 3 – Atualiza opções do dropdown com base no DataFrame carregado
@app.callback(
    Output('filtros-hover', 'options'), # Atualiza opções do dropdown com base no DataFrame carregado
    Output('filtros-hover', 'value'), # Atualiza valores selecionados no dropdown
    Input('store-data', 'data'), # Novo input para o JSON do DataFrame carregado
    Input('remover-button', 'n_clicks'), # Novo input para o botão de controle
    Input('preencher-todos-button', 'n_clicks'), # Novos inputs para os botões de controle
)
def controlar_dropdown(json_data, n_remover, n_preencher): # Função para controlar opções do dropdown com base no upload e botões de controle

    ctx = dash.callback_context # Contexto do callback para identificar qual input disparou a função

    # Se não houve trigger ainda (primeira execução)
    if not ctx.triggered: # Se nenhum input disparou o callback, usa colunas do dataset inicial para preencher opções do dropdown
        # Usa o dataset inicial carregado no começo do script
        colunas = [col for col in df.columns if col not in ['tid', 'label']] # Exclui colunas de identificação e rótulo
        options = [{'label': col, 'value': col} for col in colunas] # Cria opções para o dropdown com base nas colunas do dataset inicial
        return options, colunas # Seleciona todas as colunas do dataset inicial por padrão

    trigger = ctx.triggered[0]['prop_id'].split('.')[0] # Identifica qual input disparou o callback

    # Se veio do upload
    if trigger == 'store-data' and json_data is not None: # Se o trigger foi o upload e tem dados, atualiza opções com as colunas do dataset carregado
        df_upload = pd.read_json(StringIO(json_data), orient='split') # Converte JSON de volta para DataFrame
        colunas = [col for col in df_upload.columns if col not in ['tid', 'label']] # Exclui colunas de identificação e rótulo
        options = [{'label': col, 'value': col} for col in colunas] # Cria opções para o dropdown com base nas colunas do DataFrame carregado
        return options, colunas # Seleciona todas as colunas do upload por padrão

    # Remover
    if trigger == 'remover-button': # Se o botão "Remover Todas" foi clicado, desmarca todas as colunas
        return dash.no_update, [] # Retorna opções atuais mas desmarca todas as colunas

    # Preencher
    if trigger == 'preencher-todos-button': # Se o botão "Preencher Todas" foi clicado, seleciona todas as colunas disponíveis
        if json_data is not None: # Se tiver upload, usa colunas do dataset carregado
            df_upload = pd.read_json(StringIO(json_data), orient='split') # Se tiver upload, usa colunas do dataset carregado
            colunas = [col for col in df_upload.columns if col not in ['tid', 'label']] # Se tiver upload, usa colunas do dataset carregado
        else: # Se não tiver upload, usa colunas do dataset inicial
            colunas = [col for col in df.columns if col not in ['tid', 'label']] # Se não tiver upload, usa colunas do dataset inicial

        return dash.no_update, colunas # Retorna opções atuais mas seleciona todas as colunas

    raise dash.exceptions.PreventUpdate # Se nenhum trigger válido, não atualiza nada

# Atualiza limite máximo e texto informativo
@app.callback(
    Output('inicio-input', 'max'),
    Output('fim-input', 'max'),
    Output('info-limites-traj', 'children'),
    Input('store-data', 'data')
)
def atualizar_limites_inputs(json_data):

    if json_data is not None:
        df_base = pd.read_json(StringIO(json_data), orient='split')
        T_local, _ = df2trajectory(
            df_base,
            data_desc=None,
            tid_col='tid',
            label_col='label'
        )
    else:
        T_local = T

    total = len(T_local)

    texto_info = f"Total de trajetórias: {total}"

    return total, total, texto_info

if __name__ == '__main__':  # Só executa quando rodar o script diretamente
    app.run(debug=True)  # Roda o servidor do Dash em modo debug para desenvolvimento
    
    
    