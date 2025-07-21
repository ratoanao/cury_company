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
import numpy as np

st.set_page_config(page_title = 'Visão Restaurantes', page_icon = '🍴', layout = 'wide')

# =====================================
# Funções
# =====================================

def avg_std_time_on_traffic(df1):
    df_aux = (df1.loc[:, ['Time_taken(min)','City','Road_traffic_density']]
            .groupby(['City','Road_traffic_density'])
            .agg({'Time_taken(min)':['mean','std']}, axis = 1))
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path = ['City', 'Road_traffic_density'],
                    values = 'avg_time',
                    color = 'std_time',
                    color_continuous_scale = 'RdBu',
                    color_continuous_midpoint = np.average(df_aux['std_time']))
    return fig


def avg_std_time_graph(df1):
    df_aux = (df1.loc[:, ['Time_taken(min)','City']]
                .groupby('City')
                .agg({'Time_taken(min)' : ['mean','std']}))
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name = 'Control',
                            x = df_aux['City'],
                            y = df_aux['avg_time'],
                            error_y = dict(type = 'data', array = df_aux['std_time'])))
    fig.update_layout(barmode = 'group')
    return fig

def avg_std_time_delivery(df1, festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo
                - op: Tipo de operação que precisa ser calculado
                    'avg_tim': Calcula o tempo médio
                    'std_time: Calcula o desvio padrão do tempo.
            Output:
                - df: Dataframe com 2 colunas e 1 linha    
    """
    df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
            .groupby('Festival')
            .agg({'Time_taken(min)':['mean','std']}))

    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)
    return df_aux

def distance(df1, fig):
    if fig == False:
        colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df1['distance'] = df1.loc[:, colunas].apply(
            lambda x: haversine(
                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance
    else:
        colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, colunas].apply(
            lambda x: haversine(
                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
            ), axis=1
        )

        # Média por cidade
        avg_distance = df1.groupby('City')['distance'].mean().reset_index()

        # Gráfico de pizza
        fig = go.Figure(data = [
            go.Pie(
                labels = avg_distance['City'],
                values = avg_distance['distance'],
                pull = [0.1 if i == 1 else 0 for i in range(len(avg_distance))]  # destaque na segunda fatia
            )
        ])
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


#-------------------------------------
# Import Dataset
#-------------------------------------

df = pd.read_csv('ftc_programacao_python/train.csv')
df1 = df.copy()

# Cleaning code
df1 = clean_code(df)

# ============================================================
# Barra lateral no Streamlit
# ============================================================

st.header('Visão Restaurantes')


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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','--','--'])

with tab1:
    st.subheader('Overall Metrics')
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:

        unicos = len(df1['Delivery_person_ID'].unique())
        col1.metric('Entregadores únicos', unicos)


    with col2:
        avg_distance = distance(df1, fig = False)
        col2.metric('Distância média das entregas', avg_distance)

                
    with col3:
        df_aux = avg_std_time_delivery(df1,'Yes','avg_time')
        col3.metric('Tempo médio de entrega com Festival', df_aux)

        
            
    with col4:
        df_aux = avg_std_time_delivery(df1,'Yes','std_time')
        col4.metric('Desvio Padrão de entrega com Festival', df_aux)
        

    with col5:
        df_aux = avg_std_time_delivery(df1,'No','avg_time')
        col5.metric('Tempo médio de entrega sem Festival', df_aux)
        
        
    with col6:
        df_aux = avg_std_time_delivery(df1,'No','std_time')
        col6.metric('Desvio Padrão de entrega sem Festival', df_aux)


    st.markdown("""---""")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Distribuição do tempo por cidade')
        fig = avg_std_time_graph(df1)
        st.plotly_chart(fig)

        
    with col2:
        st.subheader('Distribuição da distância')

        df_aux = (df1.loc[:, ['Time_taken(min)','City','Type_of_order']]
                    .groupby(['City','Type_of_order'])
                    .agg({'Time_taken(min)':['mean','std']}))
        df_aux.columns = ['avg_time','std_time']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)

    st.markdown("""---""")
    st.subheader('Tempo médio de entrega por cidade')

    col1, col2 = st.columns(2)

    with col1:
        fig = distance(df1, fig = True)
        st.plotly_chart(fig)


    with col2:
        fig = avg_std_time_on_traffic(df1)
        st.plotly_chart(fig)

        
