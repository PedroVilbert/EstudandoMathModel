# Definição de funções auxiliares

def icone_avaliacao(av):  # Função para converter valor numérico de avaliação em estrelas
    
    if av is None or av == 0 or av == "-" or av == "Nan" or av == "NaN": # Verifica se a avaliação é nula, zero ou "Nan"
        return "\t -"  # Retorna símbolo de ausência de avaliação
    else:
        avaliacao = av / 2  # Divide avaliação por 2 para escalar de 0 a 5
        
        # Decide se meia estrela deve aparecer 
        if avaliacao - int(avaliacao)>= 0.5:
            meia_estrela = "⯪" # Se avaliação tem parte decimal maior ou igual a 0.5, meia estrela é representada por símbolo de meia estrela
        elif avaliacao - int(avaliacao) == 0: 
            meia_estrela = "" # Se avaliação é um número inteiro, não há meia estrela
        else:
            meia_estrela = "☆" # Se avaliação tem parte decimal menor que 0.5, meia estrela é representada por estrela cinza
    
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


def extrair_valor(coluna, p, data_desc):  # Função que retorna o valor de uma coluna para um ponto p da trajetória
    
    # Latitude (coordenada x)
    if coluna == "lat":
        return p.aspects[0].x  
    
    # Longitude (coordenada y)
    if coluna == "lon":
        return p.aspects[0].y  

    # Número sequencial do ponto
    if coluna == "Ponto":
        return p.seq  

    # Lista de atributos do dataset para encontrar o índice da coluna desejada
    atributos = [attr.name for attr in data_desc.attributes]

    try:
        idx = atributos.index(coluna)
    except ValueError:
        return ''

    aspecto = p.aspects[idx]

    # Alguns aspects possuem atributo .value
    valor = aspecto.value if hasattr(aspecto, "value") else aspecto  

    # Cria a versão numérica da avaliação indo de 0 até 5
    if coluna == "rating":
        
        if valor == "Nan" or valor == "NaN" or valor == "-" or valor is None:
            valor = 0
            
        if valor and valor > 0:
            num_avaliacao = str(valor / 2)
        else:
            num_avaliacao = "-"
        return icone_avaliacao(valor) + "\t(" + num_avaliacao + ")"

    # Clima formatado com emoji correspondente
    if coluna == "weather":
        return icones_clima(valor)

    return valor



