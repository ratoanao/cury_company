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

st.set_page_config(page_title = 'Visão Empresa', page_icon = '📊', layout = 'wide')


# =====================================
# Funções
# =====================================

def country_maps(df1):
    colunas = df1.loc[:, ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
    df_aux = (colunas.groupby(['City','Road_traffic_density'])
                .median()
                .reset_index())

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup = location_info[['City','Road_traffic_density']]).add_to(map)
    folium_static(map, width = 1024, height = 600)


def orders_per_delivery_person_per_week(df1):
    # Quantidade de pedidos por semana / quantidade de entregadores por semana
    colunas01 = ['ID','week_of_year']
    df_aux01 = (df1.loc[:, colunas01]
                .groupby(['week_of_year'])
                .count()
                .reset_index())
    colunas02 = ['Delivery_person_ID','week_of_year']
    df_aux02 = (df1.loc[:, colunas02]
                .groupby('week_of_year')
                .nunique()
                .reset_index())

    df_aux = pd.merge(df_aux01, df_aux02, how = 'inner')
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x = 'week_of_year', y = 'order_by_delivery')
    return fig

def order_per_week(df1):
    # criar a coluna de semana do ano
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = (df1.loc[:,['ID','week_of_year']]
                .groupby('week_of_year')
                .count()
                .reset_index())

    # desenhando um gráfico de linhas
    fig = px.line(df_aux, x = 'week_of_year', y = 'ID')
    return fig

def traffic_order_city(df1):
    # gráfico de bolhas
    colunas = ['ID','City','Road_traffic_density']
    df_aux = (df1.loc[:,colunas]
                .groupby(['City','Road_traffic_density'])
                .count()
                .reset_index())
    
    fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')
    return fig

def traffic_order_share(df1):
    # gráfico de pizza
    df_aux = (df1.loc[:,['ID','Road_traffic_density']]
                .groupby('Road_traffic_density')
                .count()
                .reset_index())
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    fig = px.pie(df_aux, values = 'entregas_perc', names = 'Road_traffic_density')
    return fig

def order_metric(df1):
    colunas = ['ID','Order_Date']
    # selecionando as linhas
    selecao = (df1.loc[:, colunas]
                .groupby('Order_Date')
                .count()
                .reset_index())
    selecao.head()

    # desenhando o gráfico
    fig = px.bar(selecao, x = 'Order_Date', y = 'ID')

    return fig

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



# ================================= Início da estrutura lógica do código ==================================
# =========================================================================================================

# Importando o dataset
df = pd.read_csv('ftc_programacao_python/train.csv')
df1 = df.copy()

# Limpando os dados
df1 = clean_code(df)

# ============================================================
# Barra lateral no Streamlit
# ============================================================

st.header('Marketplace - Visão Empresa')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    # Order Metric
    st.markdown('# Orders per Day')
    fig = order_metric(df1)
    st.plotly_chart(fig, use_container_width = True)

    # neste ponto não precisamos fazer o "container" pois as colunas foram divididas lateralmente com sucesso.

    col1, col2 = st.columns(2)
    with col1:
        fig = traffic_order_share(df1)
        st.header('Traffic Order Share')
        st.plotly_chart(fig, use_container_width = True)

        
    with col2: 
        fig = traffic_order_city(df1)
        st.header('Traffic Order City')
        st.plotly_chart(fig, use_container_width = True)


with tab2:
    st.header('Orders per Week')
    fig = order_per_week(df1)
    st.plotly_chart(fig, use_container_width = True)




    st.header("Orders per Delivery Person per Week")
    fig = orders_per_delivery_person_per_week(df1)
    st.plotly_chart(fig, use_container_width = True)

    

with tab3:
    st.header('Country Maps')
    country_maps(df1)
    

print('Estou aqui')


