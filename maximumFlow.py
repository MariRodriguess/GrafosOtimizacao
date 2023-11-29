# Módulo que precisa ser importado para a leitura dos arquivos CSV:
import csv
# Bibliotecas que precisam ser instaladas e importadas:
import networkx as nx                  
import matplotlib.pyplot as plt
import numpy as np

#------------------------------------------------------------------------------------------------------------------------------------------------

# Ler os dados dos arquivos CSV
def read_csv(filename):
    data = []
    with open(filename, 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            data.append(row)
    return data

# Carregar os dados dos arquivos CSV
antenas_data = read_csv('data/Antenas.csv') #Arquivo contendo as antenas e suas respectivas capacidades
clientes_data = read_csv('data/Clientes.csv') #Arquivo contendo os clientes e seus respectivos planos de internet contratados
conexoes_data = read_csv('data/ConexoesPossiveis.csv') #Arquivo contendo todas as conexões possíveis entre cliente e antena
conexoesAnt_data = read_csv('data/ConexoesAnteriores.csv') #Arquivo contendo as conexões preestabelecidas

#------------------------------------------------------------------------------------------------------------------------------------------------

#GRAFO COM TODAS AS CONEXÕES POSSÍVEIS

# Criação de um grafo direcionado
G_Possiveis = nx.DiGraph()

# Adicionar nós para antenas e clientes
for cliente in clientes_data:
    G_Possiveis.add_node(cliente['NomeCliente'], plano=int(cliente['PlanoDeInternet(Mb)']))

for antena in antenas_data:
    G_Possiveis.add_node(antena['NomeAntena'], capacity=int(antena['Capacidade(Mbps)']))

# Adicionar arestas com os pesos 
for conexao in conexoes_data:
    antena = conexao['Antena']
    cliente = conexao['Cliente']
    sinal = int(conexao['Sinal(dBm)'])
    antena_capacity = int(antenas_data[int(antena[6:]) - 1]['Capacidade(Mbps)'])
    plano = int(clientes_data[int(cliente[7:]) - 1]['PlanoDeInternet(Mb)'])
    peso = float((plano * (1 / sinal)) * (-1))
    G_Possiveis.add_edge(cliente, antena, capacity=peso, plano=plano)

# Adicionar uma origem e destino artificial
G_Possiveis.add_node('Origem')
G_Possiveis.add_node('Destino')

# Conectar a origem a cada cliente com o peso do plano do cliente
for cliente in clientes_data:
    G_Possiveis.add_edge('Origem', cliente['NomeCliente'], weight=int(cliente['PlanoDeInternet(Mb)']))

# Conectar cada antena ao destino com o peso da capacidade da antena
for antena in antenas_data:
    G_Possiveis.add_edge(antena['NomeAntena'], 'Destino', weight=int(antena['Capacidade(Mbps)']))

# Definir a posição dos nós
pos = nx.kamada_kawai_layout(G_Possiveis)

# Ajustar a posição do nó 'Origem'
pos['Origem'] = np.array([-4, -40])  # Coloca o nó 'Origem' no canto esquerdo

# Ajustar a posição dos nós 'Clientes' para espaçamento vertical
clientes_pos = {}
vertical_spacing_cliente = 1.8 
current_y_cliente = 0
for node in G_Possiveis.nodes():
    if 'Cliente' in node:
        clientes_pos[node] = np.array([0, current_y_cliente])
        current_y_cliente -= vertical_spacing_cliente

# Atualizar a posição dos nós 'Clientes'
pos.update(clientes_pos)

# Ajustar a posição dos nós 'Antenas' para espaçamento vertical
antenas_pos = {}
vertical_spacing_antena = 5  
current_y_antena = 0
for node in G_Possiveis.nodes():
    if 'Antena' in node:
        antenas_pos[node] = np.array([4, current_y_antena])
        current_y_antena -= vertical_spacing_antena

# Atualizar a posição dos nós 'Antenas'
pos.update(antenas_pos)

# Ajustar a posição do nó 'Destino'
pos['Destino'] = np.array([6, -40])  # Coloca o nó 'Destino' à direita dos nós 'Antenas'

# Desenhar o grafo
plt.figure(figsize=(15, 15))
labels = {node: node for node in G_Possiveis.nodes}
nx.draw(G_Possiveis, pos, with_labels=True, labels=labels)
edge_labels = {edge: f'{weight:.3f}' for edge, weight in nx.get_edge_attributes(G_Possiveis, 'weight').items()}
nx.draw_networkx_edge_labels(G_Possiveis, pos, edge_labels=edge_labels)
plt.title('Grafo com Todas as Conexões Possíveis Para Cada Cliente Modelado Para Rede de Fluxo')
plt.show()

#------------------------------------------------------------------------------------------------------------------------------------------------

#GRAFO COM CONEXÕES ESTABELECIDAS ANTERIORMENTE, ANTERIOR AO ALGORITMO DE FLUXO MÁXIMO

# Criação de um grafo direcionado
G_Ant = nx.Graph()

for cliente in clientes_data:
    G_Ant.add_node(cliente['NomeCliente'], plano=int(cliente['PlanoDeInternet(Mb)']))

# Adicionar nós para antenas e clientes
for antena in antenas_data:
    G_Ant.add_node(antena['NomeAntena'], capacity=int(antena['Capacidade(Mbps)']))

# Adicionar arestas com os pesos (sinal * (1 / antena_capacity))
for conexaor in conexoesAnt_data:
    antena = conexaor['Antena']
    cliente = conexaor['Cliente']
    G_Ant.add_edge(cliente, antena)

# Adicionar uma origem e destino
G_Ant.add_node('Origem')
G_Ant.add_node('Destino')

# Conectar a origem a cada cliente com o peso do plano do cliente
for cliente in clientes_data:
    G_Ant.add_edge('Origem', cliente['NomeCliente'], weight=int(cliente['PlanoDeInternet(Mb)']))

# Conectar cada antena ao destino com o peso da capacidade da antena
for antena in antenas_data:
    G_Ant.add_edge(antena['NomeAntena'], 'Destino', weight=int(antena['Capacidade(Mbps)']))

# Definir a posição dos nós
pos = nx.kamada_kawai_layout(G_Ant)

# Ajustar a posição do nó 'Origem'
pos['Origem'] = np.array([-4, -40])  # Coloca o nó 'Origem' no canto esquerdo

# Ajustar a posição dos nós 'Clientes' para espaçamento vertical
clientes_pos = {}
vertical_spacing_cliente = 1.8  
current_y_cliente = 0
for node in G_Ant.nodes():
    if 'Cliente' in node:
        clientes_pos[node] = np.array([0, current_y_cliente])
        current_y_cliente -= vertical_spacing_cliente

# Atualizar a posição dos nós 'Clientes'
pos.update(clientes_pos)

# Ajustar a posição dos nós 'Antenas' para espaçamento vertical
antenas_pos = {}
vertical_spacing_antena = 5  
current_y_antena = 0
for node in G_Ant.nodes():
    if 'Antena' in node:
        antenas_pos[node] = np.array([4, current_y_antena])
        current_y_antena -= vertical_spacing_antena

# Atualizar a posição dos nós 'Antenas'
pos.update(antenas_pos)

# Ajustar a posição do nó 'Destino'
pos['Destino'] = np.array([6, -40])  # Coloca o nó 'Destino' à direita dos nós 'Antenas'

# Desenhar o grafo
plt.figure(figsize=(15, 15))
labels = {node: node for node in G_Ant.nodes}
nx.draw(G_Ant, pos, with_labels=True, labels=labels)
edge_labels = {edge: f'{weight:.3f}' for edge, weight in nx.get_edge_attributes(G_Ant, 'weight').items()}
nx.draw_networkx_edge_labels(G_Ant, pos, edge_labels=edge_labels)
plt.title('Grafo com Todas as Conexões Estabelecidas Antes da Aplicação do Algoritmo de Fluxo Máximo')
plt.show()


#------------------------------------------------------------------------------------------------------------------------------------------------

#Aplicar o algoritmo de Edmonds-Karp no grafo
fluxo_maximo, dic = nx.maximum_flow(G_Possiveis, 'Origem', 'Destino', flow_func=nx.algorithms.flow.edmonds_karp)

#------------------------------------------------------------------------------------------------------------------------------------------------

# Criação de um arquivo CSV para inserir as conexões de maior fluxo

arquivo_resultante = 'data/ConexoesResultantes.csv'

def escreverArq(cliente, antena, sinal):
    with open(arquivo_resultante, 'a', newline='') as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv, delimiter=';')
        escritor_csv.writerow([str(cliente), str(antena), str(sinal)])

escreverArq('Cliente', 'Antena', 'Sinal(dBm)')

#------------------------------------------------------------------------------------------------------------------------------------------------

#GRAFO RESULTANTE COM AS CONEXÕES CLIENTE->ANTENA DE MAIOR FLUXO

# Criar um novo grafo para armazenar as conexões de maior fluxo
G_Pos = nx.Graph()

# Adicionar a conexão origem-cliente
for cliente in clientes_data:
    G_Pos.add_edge('Origem', cliente['NomeCliente'])

# Adicionar as conexões cliente-antena de maior fluxo
for cliente, conexoes in dic.items():
    
    if conexoes: # Verificar se há conexões para o cliente

        antena_max_fluxo = max(conexoes, key=conexoes.get) # Encontrar a antena com o maior fluxo para o cliente
        G_Pos.add_edge(cliente, antena_max_fluxo) # Adicionar a conexão cliente-antena de maior fluxo
        
        for con in conexoes_data:
            if con['Cliente'] == cliente and con['Antena'] == antena_max_fluxo:
                escreverArq(cliente, antena_max_fluxo, con['Sinal(dBm)']) #Escrever as conexões de maior fluxo no arquivo "ConexoesResultantes"

# Adicionar as conexões antena->destino do grafo original
for antena in antenas_data:
    G_Pos.add_edge(antena['NomeAntena'], 'Destino')

# Definir a posição dos nós
pos = nx.kamada_kawai_layout(G_Pos)

# Ajustar a posição do nó 'Origem'
pos['Origem'] = np.array([-4, -40])  # Coloca o nó 'Origem' no canto esquerdo

# Ajustar a posição dos nós 'Clientes' para espaçamento vertical
clientes_pos = {}
vertical_spacing_cliente = 1.8  
current_y_cliente = 0
for node in G_Pos.nodes():
    if 'Cliente' in node:
        clientes_pos[node] = np.array([0, current_y_cliente])
        current_y_cliente -= vertical_spacing_cliente

# Atualizar a posição dos nós 'Clientes'
pos.update(clientes_pos)

# Ajustar a posição dos nós 'Antenas' para espaçamento vertical
antenas_pos = {}
vertical_spacing_antena = 5  
current_y_antena = 0
for node in G_Pos.nodes():
    if 'Antena' in node:
        antenas_pos[node] = np.array([4, current_y_antena])
        current_y_antena -= vertical_spacing_antena

# Atualizar a posição dos nós 'Antenas'
pos.update(antenas_pos)

# Ajustar a posição do nó 'Destino'
pos['Destino'] = np.array([6, -40])  # Coloca o nó 'Destino' à direita dos nós 'Antenas'

# Desenhar o grafo após o algoritmo de fluxo máximo sem os pesos
plt.figure(figsize=(15, 15))
labels = {node: node for node in G_Pos.nodes}
nx.draw(G_Pos, pos, with_labels=True, labels=labels)
plt.title('Novo Grafo com Conexões de Maior Fluxo') 
plt.show()