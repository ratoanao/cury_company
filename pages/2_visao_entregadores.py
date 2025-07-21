# Importando bibliotecas

import pandas as pd
import re
from haversine import haversine
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão Entregadores', page_icon = '🛵', layout = 'wide')

# =====================================
# Funções
# =====================================

# def top_entregadores_rapidos(df1):
#     top_entregadores_rapidos = (df1.loc[:,['City','Delivery_person_ID','Time_taken(min)']]
#                                 .groupby('City')
#                                 .apply(lambda grupo: grupo.nsmallest(10, 'Time_taken(min)'))
#                                 .reset_index(drop = True))
#     st.dataframe(top_entregadores_rapidos(df1))
#     return top_entregadores_rapidos

def top_entregadores_rapidos(df1):
    df_aux1 = (
        df1.loc[:, ['City', 'Delivery_person_ID', 'Time_taken(min)']]
            .groupby('City')
            .apply(lambda grupo: grupo.nsmallest(10, 'Time_taken(min)'))
            .reset_index(drop=True))
    return df_aux1


def top_entregadores_lentos(df1):
    df_aux2 = (df1.loc[:,['City','Delivery_person_ID','Time_taken(min)']]
                                .groupby('City')
                                .apply(lambda grupo: grupo.nlargest(10, 'Time_taken(min)'))
                                .reset_index(drop = True))
    return df_aux2

def clean_code(df1):
    
    """   Esta função tem a responsabilidade de limpar o dataframe

            Tipos de limpeza:
            1. Remoção de dados NaN;
            2. Mudança do tipo da coluna de dados;
            3. Remoção dos espaços das variáveis de texto;
            4. Foramatação da coluna de datas;
            5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

            Input:Dataframe
            Output: Dataframe
    """

    # Convertendo as colunas para valores numéricos e retirando os valores nulos
    linhas_selecionadas = df1['Delivery_person_Age'].notnull()
    df1 = df1.loc[linhas_selecionadas, :]

    

    df1['Delivery_person_Age'] = pd.to_numeric(df1['Delivery_person_Age'], errors = 'coerce')
    df1 = df1[df1['Delivery_person_Age'].notnull()]
    df1['multiple_deliveries'] = pd.to_numeric(df1['multiple_deliveries'], errors = 'coerce')
    df1 = df1[df1['multiple_deliveries'].notnull()]
    # Road_traffic_density não precisou ser converido para números

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    # 1. convertendo a coluna age para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # 2. convertendo a coluna ratings para decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # 3. convertendo a coluna order_date de texto para data

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')

    # 4. Convertendo multiple_deliveries de texto para numero inteiro

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    df1 = df1.reset_index(drop = True)

    # 6. Removendo espaços nas strings com .str

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 7. Limpando a coluna 'Time_taken(min)'

    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('(min) ','')
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1


df = pd.read_csv('ftc_programacao_python/train.csv')
df1 = df.copy()

# cleaning dataset
df1 = clean_code(df)


# ============================================================
# Barra lateral no Streamlit
# ============================================================

st.header('Visão Entregadores')

# image_path = 'ftc_programacao_python\logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width = 120)


st.sidebar.markdown('# Curry - Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime(2022, 4, 2),
    min_value = datetime(2022, 2, 11),
    max_value = datetime(2022, 4, 6),
    format = 'DD-MM-YYYY')

st.header(date_slider)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium','High', 'Jam'],
    default = ['Low','Medium','High','Jam']
)
st.sidebar.markdown("""---""")
st.sidebar.markdown("#### Powered by Comunidade DS")

# Filtro de data

linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]


# Filtro de transito

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]


# ============================================================
# Layout no Streamlit
# ============================================================

tab1, tab2, tab3 = st.tabs(['Visão Geral','--','--'])

with tab1:
    col1, col2, col3, col4 = st.columns(4, gap = 'Large')
    with col1:
        # A maior idade dos entregadores
        maior_idade = df1['Delivery_person_Age'].max()
        col1.metric('Maior de idade', value = maior_idade)

    with col2:
        # A menor idade dos entregadores
        menor_idade = df1['Delivery_person_Age'].min()
        col2.metric('Menor idade', value = menor_idade)

    with col3:
        # A melhor condição de veículo
        melhor_condicao = df1['Vehicle_condition'].max()
        col3.metric('Melhor condição', value = melhor_condicao)

    with col4:
        # A pior condição de veículo
        pior_condicao = df1['Vehicle_condition'].min()
        col4.metric('Pior condição', value = pior_condicao)


    st.markdown("""---""")
    st.title('Avaliações')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('##### Avaliação média por entregador')
        avg_delivery_ratings = (df1.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
                                    .groupby('Delivery_person_ID')
                                    .mean()
                                    .reset_index())
        
        st.dataframe(avg_delivery_ratings)

    with col2:
        st.markdown('##### Avaliação média por trânsito')
        avg_delivery_traffic = (df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                    .groupby('Road_traffic_density')
                                    .agg({'Delivery_person_Ratings':['mean','std']})
                                    .reset_index())

        # Mudando os nomes das colunas
        avg_delivery_traffic.columns = ['Road_traffic_density','Delivery_mean','Delivery_std']

        st.dataframe(avg_delivery_traffic)

        st.markdown('##### Avaliação média por clima')
        avg_weatherconditions = (df1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                    .groupby('Weatherconditions')
                                    .agg({'Delivery_person_Ratings':['mean','std']})
                                    .reset_index())
        
        # Mudando os nomes das colunas
        avg_weatherconditions.columns = (['Weatherconditions','Delivery_mean','Delivery_std'])

        st.dataframe(avg_weatherconditions)


    st.markdown("""---""")

    st.title("Velocidade de entrega")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('##### Top entregadores mais rápidos')
        df3 = top_entregadores_rapidos(df1)
        st.dataframe(df3)
    

    with col2:
        st.markdown('##### Top entregadores mais lentos')
        df4 = top_entregadores_lentos(df1)
        st.dataframe(df4)

        