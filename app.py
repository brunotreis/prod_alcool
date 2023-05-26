from dash import Dash, html, dcc
import pandas as pd
import numpy as np
from scipy.integrate import odeint
import plotly.express as px
from dash.dependencies import Input, Output
import dash_renderer


app = Dash(__name__, title='Produção de Álcool')



server = app.server

"""
texto = 'Esse modelo prediz a concentração dos componentes ' \
        'células, substrato e produto (g/L) no caldo da fermentação' \
        ' alcoólica durante o tempo de processo (em horas).' \
        ' Considerou-se a levedura ${\it Saccharomyces\ \ cerevisiae}$ ' \
        'como agente biológico produtor de etanol e sacarose ' \
        'extraída da cana-de-açúcar como substrato (condição majoritariamente ' \
        'empregada na indústria brasileira). As equações fundamentais (sistema de EDO) ' \
        'foram desenvolvidas com base em hipóteses previamente adotadas para o ' \
        'processo conduzido em modo batelada alimentada e utilizou-se o modelo ' \
        'cinético hibrido de Andrews (1968) – Levenspiel (1980) que considera ' \
        'inibição por substrato e produto para representar a velocidade ' \
        'específica de crescimento celular ($\mu$).'
"""

texto= 'Este aplicativo fornece os perfis das concentrações de células' \
       ', substrato e produto e variação do volume da fase líquida ao ' \
       'longo do tempo em um processo fermentativo alcoólico de produção ' \
       'de bioetanol. O processo é conduzido em batelada alimentada, modo ' \
       'de operação empregado pela maioria das destilarias brasileiras, e ' \
       'ocorre em duas etapas: Inicialmente, mosto contendo substrato é ' \
       'alimentado à suspensão de células, denominada “pé-de-cuba”, até o ' \
       'alcance do volume útil do fermentador. Em seguida, o processo continua' \
       ' em modo batelada até que o substrato seja completamente consumido.'\
        'O modelo utilizado, apresentado na aba Equações Diferenciais, ' \
       'é constituído por um sistema de quatro equações diferenciais ordinárias, ' \
       'resultantes dos balanços de massa para os componentes células, ' \
       'substrato e produto e balanço de massa total. O modelo cinético ' \
       'híbrido de Andrews-Levenspiel, que considera inibição por substrato ' \
       'e produto, foi utilizado para representar a velocidade específica de crescimento celular ($\mu$).'




formula1 = '$\\displaystyle  \\frac{dV}{dt}= F_e$'

formula2 = '$\\displaystyle  \\frac{dC_x}{dt}= C_x (\mu - \\frac{F_e}{V})$'

formula3 = '$\\displaystyle  \\frac{dC_s}{dt}= \\frac{F_e}{V}(C_{sm}-C_s)- \\frac{\mu}{Y_{x/s}} C_x$'

formula4 = '$\\displaystyle  \\frac{dC_e}{dt}= \\frac{Y_{e/s}}{Y_{x/s}} \mu C_x - \\frac{F_e}{V} C_e$'

formula5= 'Onde $\\displaystyle \mu = \\frac{\mu_{max} C_{s}}{K_{s} + C_{s} + \\frac{C_{s}^2}{K_{is}}} \\left(1- \\frac{C_e}{C_{e_{max}}}\\right)^n$'


app.layout = html.Div(
    [
        html.Header([html.H1('Fermentação Alcoólica'), html.H2(
            'Batelada Alimentada')], id='cabeçalho'),
        html.Div([html.H3('Apresentação', id='exercicio'),
                  dcc.Tabs([
                      dcc.Tab(html.Div(dcc.Markdown(texto,  mathjax=True),
                              id='resumo'), label='Resumo'),
                      dcc.Tab(
                          html.Div([
                              dcc.Markdown(formula1,  mathjax=True),
                              dcc.Markdown(formula2,  mathjax=True),
                              dcc.Markdown(formula3,  mathjax=True),
                              dcc.Markdown(formula4,  mathjax=True),
                              html.Br(), #pular uma linha
                              dcc.Markdown(formula5,  mathjax=True)
                          ], id='equa_dif'), label='Equações Diferenciais'),
                      dcc.Tab(html.Div(html.Figure(
                          html.Img(src='/assets/fig.png', alt='Esquema Batelada Alimentada', id='fig_batelada')), id='ajuste_fig'), label='Etapas do Processo')
                  ])
                  ], className='container'),
        html.Div([
            html.Div([
                html.H4('Digite o valor final de t:', className='texto_caixa'),
                html.Div(dcc.Input(id='tempo', value=50,
                         type='number'), className='ent')
            ], className='entrada'),
            html.Div([
                html.H4(dcc.Markdown(
                    'Digite o valor de $C_{x_0}$:', mathjax=True), className='texto_caixa'),
                html.Div(dcc.Input(id='Cx0', value=30,
                         type='number'), className='ent')
            ], className='entrada'),
            html.Div([
                html.H4(dcc.Markdown(
                    'Digite o valor de $C_{s_0}$:', mathjax=True), className='texto_caixa'),
                html.Div(dcc.Input(id='Cs0', value=0,
                         type='number'), className='ent')
            ], className='entrada'),
            html.Div([
                html.H4(dcc.Markdown(
                    'Digite o valor de $C_{p_0}$:', mathjax=True), className='texto_caixa'),
                html.Div(dcc.Input(id='Cp0', value=0,
                         type='number'), className='ent')
            ], className='entrada'),
            html.Div([
                html.H4(dcc.Markdown('Digite o valor de $V_0$:',
                        mathjax=True), className='texto_caixa'),
                html.Div(dcc.Input(id='V0', value=0.6,
                         type='number'), className='ent')
            ], className='entrada'),
            html.Div([
                html.H4(dcc.Markdown(
                    'Digite o valor de $Y_{x/s}$:', mathjax=True), className='texto_caixa'),
                html.Div(dcc.Input(id='Yxs', value=0.0419,
                         type='number'), className='ent')
            ], className='entrada'),
            html.Div([
                html.H4(dcc.Markdown(
                    'Digite o valor de $Y_{e/s}$:', mathjax=True), className='texto_caixa'),
                html.Div(dcc.Input(id='Yes', value=0.444,
                         type='number'), className='ent')
            ], className='entrada'),
            html.Div([
                html.H4(dcc.Markdown(
                    'Digite o valor de $\mu_{max}$:', mathjax=True), className='texto_caixa'),
                html.Div(dcc.Input(id='Mimax', value=0.157076483470194,
                         type='number'), className='ent')
            ], className='entrada'),
            html.Div([
                html.H4(dcc.Markdown('Digite o valor de $K_s$:',
                        mathjax=True), className='texto_caixa'),
                html.Div(dcc.Input(id='Ks', value=14.35,
                         type='number'), className='ent')
            ], className='entrada'),
            html.Div([
                html.H4(dcc.Markdown(
                    'Digite o valor de $K_{is}$:', mathjax=True), className='texto_caixa'),
                html.Div(dcc.Input(id='Kis', value=170.35,
                         type='number'), className='ent')
            ], className='entrada'),
            html.Div([
                html.H4(dcc.Markdown(
                    'Digite o valor de $n$:', mathjax=True), className='texto_caixa'),
                html.Div(dcc.Input(id='nc', value=1.007717,
                         type='number'), className='ent')
            ], className='entrada'),
            html.Div([
                html.H4(dcc.Markdown(
                    'Digite o valor de $C_{e_{max}}$:', mathjax=True), className='texto_caixa'),
                html.Div(dcc.Input(id='Cemax', value=138.45,
                         type='number'), className='ent')
            ], className='entrada'),
        ], className='container2'),
        html.Div(
            dcc.Tabs([dcc.Tab(label='Todos os Gráficos', value='tab-1'), dcc.Tab(label='Células', value='tab-2'),
                      dcc.Tab(label='Substrato', value='tab-3'), dcc.Tab(label='Produto', value='tab-4'), dcc.Tab(label='Volume', value='tab-5')], id='tabs', value='tab-1', className='container')
        ),
        html.Div(dcc.Graph(id='fig', style={
                 'margin': '10px', 'padding': '10px'}), id='figura')
    ]

)


######################################################
colors = {'background': 'white'}


# Coeficiente de rendimento de substrato em celulas(gx/gs)
# Yxs = 0.0419
# Coeficiente de rendimento de substrato em etanol(gp/gs)
# Yes = 0.444
# Velocidade maxima especifica de crescimento celular (h-1)
# Mimax = 0.157076483470194
# Constante de saturaçao ou de meia velocidade (g/L)
# Ks = 14.35
# Kis = 170.35                      # Constante de inibicao pelo substrato (g/L)
# Concentracao maxima de etanol responsavel por cessar o crescimento celular (g/L)
# Cemax = 138.45

# variáveis acima são parêmetros, colocar num box

#nc = 1.007717                        # Adimensional
# Tempo de alimentaão  (h)(tempo de alimentação).
tE = 12.8440367
# Concentração de substrato no mosto (g/L)
Csm = 436.285714
VD = 2.0                                       # volume útil do biorreator (L)
#V0 = 0.6
#F = (VD-V0)/tE


# colocar todo o callback dentro do if tab1
@app.callback(
    Output(component_id='fig', component_property='figure'),
    Input('tabs', 'value'),
    Input(component_id='tempo', component_property='value'),
    Input(component_id='Cx0', component_property='value'),
    Input(component_id='Cs0', component_property='value'),
    Input(component_id='Cp0', component_property='value'),
    Input(component_id='V0', component_property='value'),
    Input(component_id='Yxs', component_property='value'),
    Input(component_id='Yes', component_property='value'),
    Input(component_id='Mimax', component_property='value'),
    Input(component_id='Ks', component_property='value'),
    Input(component_id='Kis', component_property='value'),
    Input(component_id='nc', component_property='value'),
    Input(component_id='Cemax', component_property='value')
)
def g(tab, tf, Cx0, Cs0, Cp0, V0, Yxs, Yes, Mimax, Ks, Kis,nc, Cemax):
    if (tf == None) or (Cx0 == None) or (Cs0 == None) or (Cp0 == None) or (V0 == None) or (Yxs == None) or (Yes == None) or (Mimax == None) or (Ks == None) or (Kis == None) or (Cemax == None) or (nc == None):
        fig = px.line()
        return fig
    else:
        t = np.linspace(0, tf, 1000)
        F = (VD - V0) / tE

        def g(y, t):
            Cx, Cs, Ce, V = y
            Mih = (Mimax * Cs / (Ks + Cs + (Cs ** 2) / Kis)) * \
                (1 - Ce / Cemax) ** nc
            if t < tE:
                dydt = [(Mih - (F / V)) * Cx, (Csm - Cs) * (F / V) - ((1 / Yxs) * Cx * Mih),
                        Yes / Yxs * Cx * Mih - (F / V) * Ce, F]
            else:
                dydt = [(Mih - (0 / V)) * Cx, (Csm - Cs) * (0 / V) - ((1 / Yxs) * Cx * Mih),
                        Yes / Yxs * Cx * Mih - (0 / V) * Ce, 0]
            return dydt
        # Cx0 = 30.0  # Concentração inicial de células
        # Cs0 = 0  # Concentracao Inicial de Substrato
        # Cp0 = 0.0  # Concentracao Inicial de Produto
        # V0 = 0.6  # Volume Inicial (inóculo)
        y0 = [Cx0, Cs0, Cp0, V0]  # Vetor Condicoes Iniciais
        sol = odeint(g, y0, t)
        df = pd.DataFrame()
        df['tempo (h)'] = pd.DataFrame(t)
        df['Concentração de células (g/L)'] = pd.DataFrame(sol[:, 0])
        df['Concentração de substrato (g/L)'] = pd.DataFrame(sol[:, 1])
        df['Concentração de Produto (g/L)'] = pd.DataFrame(sol[:, 2])
        df['Volume (L)'] = pd.DataFrame(sol[:, 3])
        if tab == 'tab-1':
            fig = px.line(df, x=df['tempo (h)'],
                          y=[df['Concentração de células (g/L)'], df['Concentração de substrato (g/L)'], df['Concentração de Produto (g/L)']], title='Batelada Alimentada')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background']
            )
            return fig
        if tab == 'tab-2':
            fig = px.line(
                df, x=df['tempo (h)'], y=df['Concentração de células (g/L)'], title='Concentração de Células')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
            )
            return fig
        if tab == 'tab-3':
            fig = px.line(
                df, x=df['tempo (h)'], y=df['Concentração de substrato (g/L)'], title='Concentração de Substrato')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
            )
            return fig
        if tab == 'tab-4':
            fig = px.line(
                df, x=df['tempo (h)'], y=df['Concentração de Produto (g/L)'], title='Concentração de Produto')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
            )
            return fig
        if tab == 'tab-5':
            fig = px.line(df, x=df['tempo (h)'], y=df['Volume (L)'], title='Volume')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
            )
            return fig



if __name__ == '__main__':
    app.run_server(debug=True)
