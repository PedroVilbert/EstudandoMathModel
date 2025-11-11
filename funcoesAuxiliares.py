# Definição de funções auxiliares

def icone_avaliacao(av):  # Função para converter valor numérico de avaliação em estrelas
    avaliacao = av / 2  # Divide avaliação por 2 para escalar de 0 a 5
    
    # Decide se meia estrela deve aparecer 
    if avaliacao - int(avaliacao)>= 0.5:
        meia_estrela = "⯪"
    elif avaliacao - int(avaliacao) == 0: 
        meia_estrela = ""
    else:
       meia_estrela = "☆" 
    
    
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

