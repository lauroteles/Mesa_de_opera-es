
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import io
import openpyxl as op
import xlsxwriter
from xlsxwriter import Workbook
import base64
from io import BytesIO
import io
import xlsxwriter as xlsxwriter
import datetime
import time

st.set_page_config(layout='wide')

paginas = 'Carteiras','Produtos','Home','Divisão de operadores'
selecionar = st.sidebar.radio('Selecione uma opção', paginas)


#---------------------------------- 
# Variaveis globais
def le_excel(x):
    df = pd.read_excel(x)
    return df


pl_original = le_excel('PL Total.xlsx')
controle_original = le_excel('controle.xlsx')
saldo_original = le_excel('Saldo.xlsx')
posicao_original = le_excel('Posição.xlsx')
produtos_original = le_excel('Produtos.xlsx')
cura_original = le_excel('Curva_comdinheiro.xlsx')

pl = pl_original.copy()
controle = controle_original.copy()
saldo = saldo_original.copy()
arquivo1 = posicao_original.copy()
produtos = produtos_original.copy()
curva_base = cura_original.copy()

#---------------------------------- 





#----------------------------------  ---------------------------------- ---------------------------------- ---------------------------------- 
# Pagina de Carteiras
#---------------------------------- ---------------------------------- ---------------------------------- ---------------------------------- 


#--------------------- EQUITIES
     

equities = {'ARZZ3': 4.5,
            'ASAI3':5.75,
            'CSAN3':6,
            'CSED3':5,
            'EGIE3':4.5,
            'EQTL3':6,
            'EZTC3':5.75,
            'HYPE3':6.50,
            'KEPL3':6.50,
            'MULT3':5,
            'PRIO3':8,
            'PSSA3':5.50,
            'SBSP3':4.50,
            'SLCE':6.50,
            'VALE3':10,
            'Caixa':10
            }
equities_graf= pd.DataFrame(list(equities.items()),columns=['Ativo','Proporção'])
equities_graf['Proporção'] =equities_graf['Proporção']/100

     
    #--------------------- iNCOME
   

income = {
    'POS':35,
    'Inflação':18,
    'PRE':44,
    'FundoDI':3
    }

small_caps = {
    'BPAC11':10,
    'ENEV3':4,
    'HBSA3':7,
    'IFCM3':5,
    'JALL3':10,
    'KEPL3':12,
    'MYPK3':5,
    'PRIO3':12,
    'SIMH3':8,
    'TASA4':8,
    'TUPY3':11,
    'WIZC3':5,
}
fii = {
    'BTLG11':22.30,
    'Caixa':6,
    'HGLG11':22.30,
    'KNCA11':7.25,
   ' MALL11':7.75,
   ' PLCR11':13.57,
    'RURA11':7.26,
    'TRXF11':13.57
}

dividendos = {
    'TAEE11':9,
   ' VIVT3':12,
    'BBSE3':17,
    'ABCB4':16,
   ' VBBR3':15,
   ' CPLE6':16,
   ' TRPL4':5
    }

small_caps_dataframe = pd.DataFrame(list(small_caps.items()),columns=['Ativo','Proporção'])
small_caps_dataframe['Proporção'] = small_caps_dataframe['Proporção']/100    
    #---------------------- Small caps

dividendos_dataframe = pd.DataFrame(list(dividendos.items()),columns=['Ativo','Proporção'])
dividendos_dataframe['Proporção'] = dividendos_dataframe['Proporção']/100
        #---------------------- Dividendos

fii_dataframe = pd.DataFrame(list(fii.items()),columns=['Ativo','Proporção'])
fii_dataframe['Proporção'] = fii_dataframe['Proporção']/100 
    #---------------------- FII

income_graf = pd.DataFrame(list(income.items()),columns=['Ativo','Proporção'])
income_graf['Proporção'] = income_graf['Proporção']/100
    
    #---------------------- Moderada
moderada = {ativo:0.75*income.get(ativo,0)+0.25*equities.get(ativo,0) for ativo in set(income)|set(equities)}
moderada_grafico = pd.DataFrame(list(moderada.items()),columns=['Ativo','Proporção'])
moderada_grafico['Proporção'] = moderada_grafico['Proporção']/100

   
    #-------------------- Arrojada     
arrojada = {ativo:0.60*income.get(ativo,0)+0.40*equities.get(ativo,0) for ativo in set(income)|set(equities)}   
arrojada_graf = pd.DataFrame(list(arrojada.items()),columns=['Ativo','Proporção'])
arrojada_graf['Proporção'] = arrojada_graf['Proporção']/100
 
    #------------------ Conservadora
   
conservadora = {ativo:0.87*income.get(ativo,0)+0.13*equities.get(ativo,0) for ativo in set(income)|set(equities)}   
conservadora_graf = pd.DataFrame(list(conservadora.items()),columns=['Ativo','Proporção'])
conservadora_graf['Proporção'] = conservadora_graf['Proporção']/100


if selecionar == 'Carteiras':


    #--------------------------------
    # --------Manipulação de arquivos
   

    arquivo2 = arquivo1.groupby(['CONTA','PRODUTO','ATIVO'])[['VALOR BRUTO','VALOR LÍQUIDO','QUANTIDADE']].sum().reset_index('CONTA')

    # Sidebar

    input_text = st.sidebar.text_input('Escreva o número conta')

    #---------------
    
    novo_arq = arquivo2.loc[arquivo2['CONTA']  == input_text]
    cont_df = controle.loc[controle['Unnamed: 2'] == input_text]


    #----------------

    novo_arq = novo_arq.groupby(['PRODUTO','CONTA'])[['VALOR LÍQUIDO','QUANTIDADE']].sum().reset_index()
    controle = controle.iloc[:,[1,2,3,4,5,7,8,9,12,16,17,18]]
    
    

    #------------- Manipulando arquivos para unir planilhas

    controle['Unnamed: 2'] = controle['Unnamed: 2'].astype(str)
    controle['Unnamed: 2'] = list(map(lambda x: '00' + x,controle['Unnamed: 2']))
    try:
            
        novo_controle = pd.merge(controle,novo_arq, left_on='Unnamed: 2',right_on='CONTA', how= 'outer' )
        nov_controle = controle.loc[controle['Unnamed: 2'] == input_text ]
        
        #--------------- somando PL da carteira


        qtd_ativos = novo_arq.groupby('CONTA')['QUANTIDADE'].sum().reset_index()
        pl_por_produtos = novo_arq.groupby('CONTA')['VALOR LÍQUIDO'].sum().reset_index()

        valor_liquido = pl_por_produtos.loc[0,'VALOR LÍQUIDO']

        novo_arq['Basket'] = novo_arq['QUANTIDADE']/novo_arq['VALOR LÍQUIDO']
        



        #------------------ Selecionando qual tipo de carteira

        if 'Unnamed: 12' in nov_controle.columns:
            valor_coluna = nov_controle['Unnamed: 12'].iloc[0]
        if valor_coluna == 'CON':
            moderada_graf = conservadora_graf
        elif valor_coluna == 'ARR':
            moderada_graf = arrojada_graf
        elif valor_coluna =='MOD':
            moderada_graf = moderada_grafico
        elif valor_coluna == 'INC':
            moderada_graf = income_graf
        elif valor_coluna == 'EQT':
            moderada_graf = equities_graf 
        elif valor_coluna == 'SMLL':
            moderada_graf = small_caps_dataframe                  
        elif valor_coluna == 'FII':
            moderada_graf = fii_dataframe   
        elif valor_coluna == 'DIV':
            moderada_graf = dividendos_dataframe   
        else:
           st.success('Essa carteira e exeção')
    
        
        st.text('Valor total da carteira')
        st.title(f'{valor_liquido:,.2f}')
        

        moderada_graf['Valor Distribuido'] = moderada_graf['Proporção']*valor_liquido





        #-----------------acertando valores em ordem e retirando colunas

        distribuicao_alvo = moderada_graf[['Ativo','Valor Distribuido']].reset_index()
        distribuicao_alvo['Ativo']=distribuicao_alvo['Ativo'].str.upper()
        distribuicao_alvo = distribuicao_alvo.sort_values(by='Ativo')
        distribuicao_alvo = distribuicao_alvo.drop(columns='index')

        novo_arq = novo_arq.sort_values(by='PRODUTO')
        novo_arq = novo_arq.drop(columns='CONTA')
        arquivo_basket = pd.merge(distribuicao_alvo,novo_arq, left_on='Ativo',right_on='PRODUTO',how='outer')
        arquivo_basket['Quantidade Ideal'] = arquivo_basket['Basket']*arquivo_basket['Valor Distribuido']
        arquivo_basket = arquivo_basket[['Ativo', 'Valor Distribuido','Quantidade Ideal']]


       #-------------------filtrando RV x RF

        lista_acoes = ['ARZZ3','ARZZ',
            'ASAI3',
            'CSAN3',
            'CSED3',
            'EGIE3',
            'EQTL3',
            'EZTC3',
            'HYPE3',
            'KEPL3',
            'MULT3',
            'PRIO3',
            'PSSA3',
            'SBSP3',
            'SLCE3',
            'VALE3',
            'Caixa']
    
        filtro_rv = novo_arq[novo_arq['PRODUTO'].isin(lista_acoes)].reset_index()
        filtro_rf = novo_arq[~novo_arq['PRODUTO'].isin(lista_acoes)].reset_index()

        filtro_rv_BASE = moderada_graf[moderada_graf['Ativo'].isin(lista_acoes)].reset_index()
        
        filtro_rf_BASE = moderada_graf[~moderada_graf['Ativo'].isin(lista_acoes)].reset_index()

        base_df_rf = arquivo_basket[arquivo_basket['Ativo'].isin(lista_acoes)].reset_index()
        base_df_rv = arquivo_basket[~arquivo_basket['Ativo'].isin(lista_acoes)].reset_index()

        filtro_total_rvrf = novo_arq[novo_arq['PRODUTO'].isin(lista_acoes)].sum().reset_index()
        analise_rvrf = novo_arq[~novo_arq['PRODUTO'].isin(lista_acoes)].sum().reset_index()


        # renda_v_vs_rf = pd.concat([filtro_total_rvrf,analise_rvrf],axis=0).reset_index()
        # renda_v_vs_rf.drop([0,2,3,4,6,7],inplace=True)
        # renda_v_vs_rf = renda_v_vs_rf.rename(columns={
        #     'index':'PRODUTO',0:'VALOR LÍQUIDO'
        #                     }).reset_index()
        # renda_v_vs_rf.at[0,'PRODUTO'] = 'Renda Variavel'
        # renda_v_vs_rf.at[1,'PRODUTO'] = 'Renda Fixa'
        # renda_v_vs_rf = renda_v_vs_rf[[
        #     'PRODUTO','VALOR LÍQUIDO']]
          


        # ideal_proporção_rf = moderada_graf[moderada_graf['Ativo'].isin(lista_acoes)].sum().reset_index()
        # ideal_proporção_rv = moderada_graf[~moderada_graf['Ativo'].isin(lista_acoes)].sum().reset_index()

        # ideal_porporção = pd.concat([ideal_proporção_rf,ideal_proporção_rv],axis=0).reset_index()
        # ideal_porporção.drop([0,2,3,5],inplace=True)
        # ideal_porporção.drop(columns='level_0')
        # ideal_porporção = ideal_porporção.rename(columns={
        #     'index':'Ativo',0:'Proporção'
        # })       
        # ideal_porporção.at[1,'Ativo'] = 'Renda Variável'
        # ideal_porporção.at[4,'Ativo'] = 'Renda Fixa'
        # ideal_porporção=ideal_porporção[['Ativo','Proporção']].reset_index()
        # ideal_porporção=ideal_porporção[['Ativo','Proporção']]

        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        mostrar_rv = st.toggle('Mostrar apenas renda variavel')
        mostrar_rf = st.toggle('Mostrar apenas renda fixa')
        st.markdown("<br>",unsafe_allow_html=True)
        #mostrarvxrf = st.toggle('Mostrar proporção Renda Fixa x Renda Variável')


        if mostrar_rv and mostrar_rf:
            novo_arq = novo_arq
            moderada_graf = moderada_graf
            arquivo_basket = arquivo_basket

        elif mostrar_rv:
            novo_arq = filtro_rv
            moderada_graf =filtro_rv_BASE
            arquivo_basket = base_df_rf

        elif mostrar_rf:
            novo_arq = filtro_rf
            moderada_graf = filtro_rf_BASE
            arquivo_basket = base_df_rv
        else:
            novo_arq = novo_arq
            moderada_graf = moderada_graf
            arquivo_basket = arquivo_basket            

        # elif mostrarvxrf:
        #     novo_arq  =  renda_v_vs_rf
        #     moderada_graf = ideal_porporção
        #     arquivo_basket = ideal_porporção

        
 
  

        #---------------------------
        #        Graficos

        

        graf1 = go.Figure(data=[go.Pie(labels=novo_arq['PRODUTO'],
                                        values=novo_arq['VALOR LÍQUIDO'],
                                        hole=0.4,
                                        textinfo='label+percent',
                                        insidetextorientation='radial',
                                        textposition='outside'
                                        )])


        figas=px.pie(moderada_graf,values='Proporção',labels='Ativo')

        graf_moderada = go.Figure(data=[go.Pie(labels=moderada_graf['Ativo'], values=moderada_graf['Proporção'],
                                                         hole=0.4,
                                        textinfo='label+percent',
                                        insidetextorientation='radial',
                                        textposition='outside'
                                        )])
        graf1.update_layout(title='Posição atual da carteira')
        graf_moderada.update_layout(title = 'Carteira balanceada')



        nov_controle = nov_controle.rename(columns={
            'Unnamed: 1':'Nome do cliente',
            'Unnamed: 2':'Conta',
              'Unnamed: 3':'Escritorio',
                'Unnamed: 4':'Estado',
                  'Unnamed: 5':'Assessor',
       'Backoffice/ Mesa':'Status',
         'Mesa de Operação.1':'Situação',
         'Backoffice.1':'Exeção',
           'Unnamed: 12':'Perfil',
       'Mesa de Operação.2':'Lembretes mesa',
         'Gestão/ Head comercial':'Observações',
           'Backoffice ':'Observações'
        })
        nov_controle = nov_controle.unstack()
        
        # -------------- Criando arquivo para Basket
        
        basket = pd.merge(arquivo_basket,novo_arq,left_on='Ativo',right_on='PRODUTO',how='inner').reset_index()
        
        precos_mercado = {}

        basket['Basket_BTG'] = basket['Quantidade Ideal']-basket['QUANTIDADE']
        basket = basket[[
            'Ativo',  'Basket_BTG']]
        basket['C/V'] = np.where(basket['Basket_BTG']<0,'V','C')
        basket['Basket_BTG'] = np.where(basket['Basket_BTG']<0,basket['Basket_BTG'].astype(int).astype(str).str[1:],basket['Basket_BTG'])
        basket['Conta'] = input_text
        basket['Validade'] = 'DIA'
        basket['Basket_BTG'] =basket['Basket_BTG'].astype(int)
       
        for ativo in basket['Ativo']:
            ticker = yf.Ticker(ativo +'.SA')
            preco_atual = ticker.history(period='5m')['Close'].iloc[-1]
       
            precos_mercado[ativo] = preco_atual
        basket['Preço'] = ''
        basket['Preço'] = basket['Ativo'].map(precos_mercado)

        basket= basket.rename(columns={
            'Basket_BTG':'Quantidade',
        })
        basket = basket [['Ativo','C/V','Quantidade','Preço','Conta','Validade']]

        data_e_hora = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        nome_arquivo = f'{data_e_hora}_{input_text}.xlsx'

        if basket is not None:
            
            
            # Use io.BytesIO para criar um buffer de bytes
            output4 = io.BytesIO()
            # Salve o DataFrame no buffer no formato XLSX
            with pd.ExcelWriter(output4, engine='xlsxwriter') as writer:
                basket.to_excel(writer,
                                            sheet_name='Basket',
                                              index=False)
            
            # Crie um link para download
            output4.seek(0)
            st.download_button(type='primary',
                label="Basket Download",
                data=output4,
                file_name=nome_arquivo,
                key='download_button')
        

        #---------------------------------------------------
        #---------------------- Ajustando graficos e tabelas
        print(novo_arq.columns)
        novo_arq = novo_arq[['PRODUTO','VALOR LÍQUIDO', 'QUANTIDADE']]
        novo_arq = novo_arq.rename(columns={
            'PRODUTO':'Ativo', 
            'QUANTIDADE':'Quantidade',
            'VALOR LÍQUIDO':'Valor em R$'
        })
        arquivo_basket = arquivo_basket.rename(columns={
            'Valor Distribuido':'Valor em R$',
            'Quantidade Ideal':'Quantidade'
        })

        arquivo_basket['Valor em R$'] = arquivo_basket['Valor em R$'].apply(lambda x: round (x, 2))
        arquivo_basket['Quantidade'] = arquivo_basket['Quantidade'].astype(str).str[:-14]

         

        #----------------------------------------------
        #---------------------- Streamlit visualization



        col1, col2 = st.columns(2)

        # -------------Coluna 1

        with col1: st.subheader('Proporção da carteira')
        with col1: st.plotly_chart(graf1,use_container_width= True)
        with col1: st.dataframe(novo_arq,use_container_width=True)
        with col1: ''
        with col1: ''
        with col1: st.subheader('Informações do cliente')
        with col1: st.dataframe(nov_controle,use_container_width=True)
        with col1: ''
        with col1: st.subheader('Basket')        
        with col1: st.dataframe(basket,use_container_width=True)

        # --------------Coluna 2

        with col2: st.subheader('Proporção ideal')
        with col2: st.plotly_chart(graf_moderada,use_container_width=True)
        with col2: st.dataframe(arquivo_basket,use_container_width=True)

        #3 --------------- ROW

    except:
        st.header('Digite uma conta valida')



#----------------------------------  ---------------------------------- ---------------------------------- ---------------------------------- 
# Pagina de produtos
#---------------------------------- ---------------------------------- ---------------------------------- ---------------------------------- 

if selecionar == 'Produtos':
    st.balloons()
    produtos = pd.read_excel('Produtos.xlsx')
    produtos = produtos[[
       'PRODUTO', 'PRAZO/VENCIMENTO', 'TAXA','TAXA EQ. CDB']]
    
    produtos['PRODUTO'] = produtos['PRODUTO'].fillna(0)
    produtos = produtos[produtos['PRODUTO'] !=0]


    #----------------------------------
    # Seleção para filtragem de produtos

    radio = ['CDB','LCA','LCI','LC']
    lc =st.sidebar.radio('selecione o tipo de produto',radio)
    pre_pos =st.radio('',['PRÉ','PÓS'])

    if lc =='CDB':
        produtos = produtos[produtos['PRODUTO'].str.slice(0,3) == 'CDB']
        if pre_pos == 'PRÉ':
            produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'CDB - PRÉ']
        elif pre_pos == 'PÓS':
           produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'CDB - PÓS']  

    elif lc == 'LCI':
        produtos = produtos[produtos['PRODUTO'].str.slice(0,3) =='LCI']
        if pre_pos == 'PRÉ':
            produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCI - PRÉ']
        elif pre_pos == 'PÓS':
           produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCI - PÓS']  
    
    elif lc == 'LC':
        produtos = produtos[produtos['PRODUTO'].str.slice(0,2) =='LC ']
        if pre_pos == 'PRÉ':
            produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'LC - PRÉ']
        elif pre_pos == 'PÓS':
           produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'LC - PÓS']          
    
    elif lc == 'LCA':
        produtos = produtos[produtos['PRODUTO'].str.slice(0,3) =='LCA']
        if pre_pos == 'PRÉ':
            produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCA - PRÉ']
        elif pre_pos == 'PÓS':
           produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCA - PÓS']

    produtos['PRE_POS'] = pre_pos
    produtos['PRODUTO'] = pd.Categorical(produtos['PRODUTO'], categories=produtos['PRODUTO'].unique(),ordered=True)
    produtos['PRE_POS'] = pd.Categorical(produtos['PRE_POS'],categories=['PRÉ','PÓS'],ordered=True)

    #----------------------------------
    # Retirando letras

    produtos['PRAZO/VENCIMENTO'] = produtos['PRAZO/VENCIMENTO'].str.extract('(\d+)').astype(float)
    produtos['TAXA EQ. CDB'] = produtos['TAXA EQ. CDB'].astype(str).str.extract('([\d,]+)')
    produtos['TAXA EQ. CDB'] = produtos['TAXA EQ. CDB'].str.replace(',','.').astype(float)


    produtos['PRAZO/VENCIMENTO'] = produtos['PRAZO/VENCIMENTO'].sort_values(ascending=True)
    produtos['TAXA EQ. CDB'] = produtos['TAXA EQ. CDB'].sort_values(ascending=True)
    #produtos = produtos.loc[produtos['PRAZO/VENCIMENTO']<1080]
    produtos['PRODUTO'] =produtos['PRODUTO'].str[:-13]
    produtos['PRODUTO'] =produtos['PRODUTO'].str[16:]

 #   produtos['prazo_em_anos'] = pd.to_datetime(produtos['PRAZO/VENCIMENTO'], unit='D').dt.to_period('M')

    produtos['Vencimento'] = datetime.datetime.now() + pd.to_timedelta(produtos['PRAZO/VENCIMENTO'],unit='D')
    produtos['Vencimento'] = produtos['Vencimento'].dt.strftime('%Y-%m-%d')
                                                                
    #----------------------------------
    #Calculando a curva 

    fig2=go.Figure()
    fig2.add_traces(go.Scatter(x=curva_base['Data'],
                        y=curva_base['Taxa Spot'],
                        mode='lines',
                        name='PREF',
                        line=dict(color='orange')
                        ))     


    #----------------------------------
    #Graficos
    
    
    #----------------------------------
    #Scatter graph com curva:

 
    fig = go.Figure()
    if pre_pos == 'PRÉ':    
        fig.add_trace(
            go.Scatter(
                x=produtos['Vencimento'],
                y=produtos['TAXA EQ. CDB'],
                mode='markers',
                marker=dict(
                size = 8,
                color = 'grey'     
                ),
                text=produtos.apply(
                    lambda row: f'O vencimento e em:  **{row["Vencimento"]}** e a Taxa do produto é:  **{row["TAXA EQ. CDB"]:.2f}%**  e o Banco emissor:  **{row["PRODUTO"]}**',axis=1),
                
            )
        )

    else:
        fig.add_trace(
            go.Scatter(
                x=produtos['PRODUTO'],
                y=produtos['TAXA EQ. CDB'],
                mode='markers',
                marker=dict(
                size = 8,
                color = 'grey'     
                ),
               text=produtos.apply(
                    lambda row: f'O praze de vencimento e em:  {row["Vencimento"]}  dias   e a Taxa do produto é:  {row["TAXA EQ. CDB"]:.2f}%  e o Banco emissor:  {row["PRODUTO"]}',axis=1),
               
        )
    )
    fig.update_layout(
        showlegend= False,
        title = 'Produtos ofertadors',
        shapes =[dict(
            type='line',
            y0=100,
            y1=100,
            x0=0,
            x1=1,
            xref='paper',
            yref='y',
            line=dict(color='#FF8C00',width=2,dash='dash')
        )
        ]
    )
    if pre_pos =='PRÉ':
        fig.update_yaxes(range=[8.5,13])

    else:
        fig.update_yaxes(range=[95,125])
   

    fig.update_xaxes(showticklabels = False)

    fig3 = go.Figure(data=fig.data+fig2.data)

    if pre_pos == 'PRÉ':
        st.plotly_chart(fig3,use_container_width=True)
    else:
        st.plotly_chart(fig,use_container_width=True)

    st.dataframe(produtos)               

#----------------------------------  ---------------------------------- ---------------------------------- ---------------------------------- 
# Pagina de divisão de contas por operador
#---------------------------------- ---------------------------------- ---------------------------------- ---------------------------------- 

if selecionar == 'Divisão de operadores':


        #####       Limpando arquivo e retirando colunas

        pl = pl.drop(columns='NOME')
        saldo = saldo.drop(columns='NOME')

        
        controle =  controle.iloc[:,[1,2,6,7,12,16,17,18,-1]]
       
        
        
        controle = controle.rename(columns = {'Unnamed: 2':'CONTA'})

        controle = controle.rename(columns= 
                                            {'Mesa de Operação':'Operador'})

        ####        Mesclando arquivos e adicionando variaveis

        juncao = pd.merge(pl,saldo,
                        how='outer',
                            on= 'CONTA')
        # Filtros para adicionar operadores

        filtro_nov1 =  juncao.SALDO> 1000
        filtro_nov2 = juncao.SALDO < 0
        
        juncao = juncao.loc[(
            filtro_nov1|filtro_nov2
            )]


        ###         Adicionando 00 para mesclar os arquivos ###
        controle['CONTA']=controle['CONTA'].astype(str)


        controle['CONTA'] = list(
            map(
                lambda x:'00'+ x,controle['CONTA']
                )
                    )


        arquivo_final = pd.merge(
            controle,juncao,
            on='CONTA',
            how= 'outer'
        )
            ####        Mesclando arquivos e adicionando variaveis

    # Filtros para adicionar operadores

        #Filtro Breno
        filtro = (arquivo_final['VALOR']<200000) & (arquivo_final['Operador']=='Edu')
        arquivo_final.loc[filtro,'Operador'] ='Breno'

        #Filtro Edu

        filtro2 =  filtro = (arquivo_final['VALOR']>200000) & (arquivo_final['Operador']=='Edu')
        arquivo_final.loc[filtro2,'Operador'] = 'Edu'

        #filtro Bruno

        filtro4 = (arquivo_final['VALOR']<200000) & (arquivo_final['Operador']=='Léo')
        arquivo_final.loc[filtro4,'Operador'] ='Bruno'
        
        # Filtro léo
        filtro6  = (arquivo_final['VALOR']>200000) & (arquivo_final['Operador']=='Léo')
        arquivo_final.loc[filtro6,'Operador'] = 'Léo'

        filtro7 = (arquivo_final['VALOR']>200000)&(arquivo_final['Operador'] =='Breno')
        arquivo_final.loc[filtro7,'Operador'] = 'Edu'

        filtro8 = (arquivo_final['VALOR']>200000)&(arquivo_final['Operador'] =='Bruno')
        arquivo_final.loc[filtro8,'Operador'] = 'Léo'

        
        
        #st.subheader('Este e o novo filtro')
        
        filtro_de_saldo = ((arquivo_final['SALDO']>1000)|(arquivo_final['SALDO']<0))
        arquivo_final2 = arquivo_final.loc[filtro_de_saldo]

        arquivo_final2['Operador'] = arquivo_final2['Operador'].fillna('Checar conta')
        arquivo_final2['Backoffice/ Mesa'] = arquivo_final2['Backoffice/ Mesa'].fillna('Checar conta')
    
       
        #### Criando funcao para alterar o nome dos operardores de acordo com criterios #### 
    
        
        arquivo_final2 = arquivo_final2.reset_index()
        
        arquivo_final2 = arquivo_final2.sort_values(by='SALDO',ascending=False)
        
        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'Mesa de Operação.2':'Lembretes Mesa'})

        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'VALOR':'BTG PL'})
        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'Saldo':'Saldo Disponivel'})
        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'Unnamed: 1':'Nome'})
        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'Backoffice/ Mesa':'Status'})
        #>>>>25/10  'Backoffice/ Mesa'
        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'Unnamed: 12':'Perfil da Carteira'})
        arquivo_final2 = arquivo_final2.rename(columns=
                                    {'Unnamed: 35':'PL Desatualizado'})
        
        arquivo_final2 = arquivo_final2.loc[(arquivo_final2['Status'] == 'Ativo') | (arquivo_final2['Status'] == 'Pode Operar')| (arquivo_final2['Status'] == 'Checar conta')]

        
        arquivo_final2 = arquivo_final2.iloc[:,[2,1,11,5,6,7,8,9,10,4,3]]


        
        arquivo_final2.insert(loc = 0,
                            column='Checkbox',
                            value=st.checkbox('arquivo_final2'
                                            )
                                            )


        barra1 = st.selectbox('Selecione o Operador',
                            options=arquivo_final2['Operador'].unique())

        df7 = arquivo_final2.loc[arquivo_final2['Operador'] == barra1]
        df6 = arquivo_final2['Operador'].value_counts()
        
        data_frame_of = st.data_editor(df7,
                                    width=2000,
                                    height=500,
                                    num_rows='dynamic')
         
        if arquivo_final2 is not None:
            
            
            # Use io.BytesIO para criar um buffer de bytes
            output4 = io.BytesIO()

            # Salve o DataFrame no buffer no formato XLSX
            with pd.ExcelWriter(output4, engine='xlsxwriter') as writer:
                arquivo_final2.to_excel(writer,
                                            sheet_name='Divisão_de_operadores.xlsx',
                                              index=False)
            
            # Crie um link para download
            output4.seek(0)
            st.download_button(
                label="Exportar dados",
                data=output4,
                file_name='Dvisão de contas por operador.xlsx',
                key='download_button'
            )
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)

        col1,col2,col3,col4,col5 = st.columns(5)

        class Contas_Operadas:
            def __init__(self, numero_da_conta, nome_do_cliente, operador_da_conta, horario_da_operação):
                self.numero_da_conta = numero_da_conta
                self.nome_do_cliente = nome_do_cliente
                self.operador_da_conta = operador_da_conta
                self.horario_da_operação = horario_da_operação

        def processar_registro_de_conta_e_operador_resposavel(numero_da_conta,operador_da_conta):
            nome_do_cliente = arquivo_final2.loc[arquivo_final2['CONTA'] == numero_da_conta,'Nome'].iloc[0]
            horario_da_operação = datetime.datetime.now().strftime('%d-%m-%Y_%H')
            conta_operada = Contas_Operadas(numero_da_conta,nome_do_cliente,operador_da_conta,horario_da_operação)
            excel_file = 'contas_operadas.xlsx'
            df_combined = pd.DataFrame()
            try:
                df_existing = pd.read_excel(excel_file)
                df_new = pd.DataFrame([conta_operada.__dict__])
                df_combined = pd.concat([df_existing,df_new],ignore_index=True).copy()
            except FileNotFoundError:
                ''

            df_combined.to_excel(excel_file,index=False)

            if botao_de_registro:
                st.success(f'Operador e conta registrada')


        possiveis_operadores_para_registro = ['Breno','Edu','Leo','Bruno']        
        with col1:numero_da_conta = st.text_input('Numero da Conta')
        with col1:operador_da_conta = st.text_input('Quem operou')
        botao_de_registro = st.button('registrar Conta Operada',type='primary')

        st.markdown("<br>",unsafe_allow_html=True)
        if botao_de_registro and numero_da_conta and operador_da_conta:
            processar_registro_de_conta_e_operador_resposavel(numero_da_conta,operador_da_conta)


        contas_operadas = pd.read_excel('contas_operadas.xlsx')
        contas_operadas = contas_operadas.sort_index(ascending = False)
        contas_operadas['horario_da_operação'] = pd.to_datetime(contas_operadas['horario_da_operação'],format='%d-%m-%Y_%H',errors='coerce')

        contas_operadas_today = contas_operadas.loc[contas_operadas['horario_da_operação'].dt.date == datetime.datetime.now().date()]
        contas_operadas_today = contas_operadas_today.sort_values(by='horario_da_operação', ascending=False)
        print(contas_operadas.columns)
        st.dataframe(contas_operadas_today)

        if arquivo_final2 is not None:
            
            
            # Use io.BytesIO para criar um buffer de bytes
            output12 = io.BytesIO()

            # Salve o DataFrame no buffer no formato XLSX
            with pd.ExcelWriter(output12, engine='xlsxwriter') as writer:
                contas_operadas.to_excel(writer,
                                            sheet_name='Contas_operadas.xlsx',
                                              index=False)
            
            # Crie um link para download
            output12.seek(0)
            st.download_button(
                label="Exportar dados",
                data=output12,
                file_name='Contas_operadas.xlsx',
                key='download_button_contas_operadas',
            )                  


