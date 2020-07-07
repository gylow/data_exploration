import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import base64

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href



def main():
    st.image('logo.png', width=200)
    st.title('AceleraDev Data Science')
    st.subheader('Semana 3 - Análise de dados exploratória')

    #data_load_state = st.text('Loading data...')
    #data = load_data(10000)
    #data_load_state.text("Done! (using st.cache)")


    file_in = st.file_uploader('Escolha um arquivo "csv":', type='csv')
    if file_in is not None:
        df = st.cache(pd.read_csv)(file_in)
        n_lin, n_col = df.shape
        aux = pd.DataFrame({'types': df.dtypes,
                            'NA #': df.isna().sum(),
                            'NA %': (df.isna().sum()/n_lin*100)})
        aux.reset_index(inplace=True)
        aux.rename(columns={'index': 'names'}, inplace=True)      
        num_cols = list(aux[aux['types'] != 'object']['names'])
        cat_cols = list(aux[aux['types'] == 'object']['names'])
        cols = list(df.columns)

        st.markdown('**Número de linhas e colunas**')        
        st.markdown('{} linhas e {} colunas'.format(n_lin, n_col))

        max_lin_slider = n_lin if n_lin < 100 else 100
        slider = st.slider('Escolha a quantidade de linhas para espiar:',
                           min_value=1, max_value=max_lin_slider, value=10)
        st.dataframe(df.head(slider))

        st.markdown(f'**Nomes das {len(cat_cols)} colunas categóricas:**')
        st.text(str(cat_cols).strip('[]').replace('\'', ''))

        st.markdown(f'**Nomes das {len(num_cols)} colunas núméricas:**')
        st.text(str(num_cols).strip('[]').replace('\'', ''))

        st.markdown('**Informações das colunas:**')
        st.table(aux)

        st.markdown('**Detalhes das colunas numéricas:**')
        transpose = '.T' if st.checkbox('Transpor detalhes') else ''
        st.dataframe(eval(f'df.describe(){transpose}'))
        



        st.subheader('Análise univariada')
        selected_column = st.selectbox('Escolha uma coluna para análise univariada:',
                                       list(aux[aux['types'] != 'object']['names']))
        hist_bin = 100 if (df[selected_column].nunique() <= 100)\
            else round(df[selected_column].nunique() / 10)
        hist_values = np.histogram(df[selected_column], bins=hist_bin)
        hist_frame = pd.DataFrame(hist_values[0], index=hist_values[1][:-1])
        st.bar_chart(hist_frame)

        col_describe = df[selected_column].describe()
        col_more = pd.Series({'skew': df[selected_column].skew(),
                              'kurtosis': df[selected_column].kurtosis()},
                             name=col_describe.name)
        st.write(pd.concat([col_more, col_describe]))

        st.subheader('Cálculos das colunas numéricas:')
        typeCalc = {'Média': '.mean()',
                    'Mediana': '.median()',
                    'Desvio Padrão': '.std()'}
        calc_choosed = st.selectbox('Escolha o tipo de cálculo para as colunas numéricas:',
                                    ['', 'Média', 'Mediana', 'Desvio Padrão'])
        if calc_choosed != '':
            exec("st.table(df[num_cols]{0})"
                 .format(typeCalc[calc_choosed]))

        st.markdown('**Percentual dos dados faltantes:**')
        st.table(aux[aux['NA #'] != 0]
                 [['types', 'NA %']])

        st.subheader('Imputação de dados numéricos faltantes')
        percentage = st.slider('Escolha o limite percentual faltante das colunas a serem prenchidas:',
                               min_value=0, max_value=100, value=0)
        col_list = list(
            aux[aux['NA %'] <= percentage]['names'])

        select_method = st.radio('Escolha um método de preenchimento:',
                                 ('Média', 'Mediana'))
        imputed_df = df[col_list].fillna(df[col_list].mean() if
                                         select_method == 'Média' else df[col_list].median())
        impputed_exploration = pd.DataFrame({'names': imputed_df.columns,
                                             'types': imputed_df.dtypes,
                                             'NA #': imputed_df.isna().sum(),
                                             'NA %': (imputed_df.isna().sum() / n_lin * 100)})
        st.table(
            impputed_exploration[impputed_exploration['types'] != 'object']['NA %'])

        st.subheader('Arquivo com os dados imputados:')
        st.markdown(get_table_download_link(
            imputed_df), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
