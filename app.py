from dash import Dash, html, dcc
import pandas as pd
import numpy as np
from scipy.integrate import odeint
import plotly.express as px
from dash.dependencies import Input, Output

app = Dash(__name__, title='Produção de Álcool')

server = app.server

texto = 'Equações'

formula1 = '$\\displaystyle  \\frac{dV}{dt}= F_e$'

formula2 = '$\\displaystyle  \\frac{dC_x}{dt}= C_x (\mu - \\frac{F_e}{V})$'

formula3 = '$\\displaystyle  \\frac{dC_s}{dt}= \\frac{F_e}{V}(C_{sm}-C_s)- \\frac{\mu}{Y_{x/s}} C_x$'

formula4 = '$\\displaystyle  \\frac{dC_e}{dt}= \\frac{Y_{e/s}}{Y_{x/s}} \mu C_x - \\frac{F_e}{V} C_e$'



app.layout = html.Div(
    [
        html.Div(html.H1('Batelada Alimentada'),id= 'cabeçalho'),
        html.Div([html.H3('Equações', id='exercicio'), html.P(dcc.Markdown(texto,  mathjax=True)), html.P(dcc.Markdown(formula1,  mathjax=True)),html.P(dcc.Markdown(formula2,  mathjax=True)), html.P(dcc.Markdown(formula3,  mathjax=True)),html.P(dcc.Markdown(formula4,  mathjax=True))],className= 'container'),
        html.Div([html.Div([html.H4('Digite o valor final de t:', className='texto_caixa'),html.Div(dcc.Input(id='tempo', value=50, type='number'), className='ent')],className='entrada'), html.Div([html.H4(dcc.Markdown('Digite o valor de $C_{x_0}$:', mathjax=True),className='texto_caixa'), html.Div(dcc.Input(id='Cx0', value=30, type='number'),className='ent')],className='entrada'), html.Div([html.H4(dcc.Markdown('Digite o valor de $C_{s_0}$:', mathjax=True), className='texto_caixa'), html.Div(dcc.Input(id='Cs0', value=0, type='number'), className='ent')],className='entrada' ), html.Div([html.H4(dcc.Markdown('Digite o valor de $C_{p_0}$:', mathjax=True), className='texto_caixa'), html.Div(dcc.Input(id='Cp0', value=0, type='number'),className='ent')],className='entrada' ), html.Div([html.H4(dcc.Markdown('Digite o valor de $V_0$:', mathjax=True), className='texto_caixa'), html.Div(dcc.Input(id='V0', value=0.6, type='number'),className='ent')],className='entrada' )],className='container2'),
        html.Div(
            dcc.Tabs([dcc.Tab(label='Todos os Gráficos', value='tab-1'), dcc.Tab(label='Células', value='tab-2'),
                      dcc.Tab(label='Substrato', value='tab-3'), dcc.Tab(label='Produto', value='tab-4'),dcc.Tab(label='Volume', value='tab-5')], id='tabs', value='tab-1', className='container')
        ),
        html.Div(dcc.Graph(id='fig', style={'margin':'10px', 'padding': '10px'}), id='figura')
    ]

)

colors = {'background': '#d3d3d3'}

Yxs = 0.0419                                # Coeficiente de rendimento de substrato em celulas(gx/gs)
Yes = 0.444                   # Coeficiente de rendimento de substrato em etanol(gp/gs)
Mimax = 0.157076483470194         # Velocidade maxima especifica de crescimento celular (h-1)
Ks = 14.35                   # Constante de saturaçao ou de meia velocidade (g/L)
Kis = 170.35                      # Constante de inibicao pelo substrato (g/L)
Cemax = 138.45                     # Concentracao maxima de etanol responsavel por cessar o crescimento celular (g/L)

#variáveis acima são parêmetros, colocar num box

nc = 1.007717                        # Adimensional
tE = 12.8440367                                     # Tempo de alimentaão  (h)(tempo de alimentação).
Csm = 436.285714                                     # Concentração de substrato no mosto (g/L)
VD = 2.0                                       # volume útil do biorreator (L)
V0= 0.6
F = (VD-V0)/tE






#colocar todo o callback dentro do if tab1
@app.callback(
    Output(component_id='fig', component_property='figure'),
    Input('tabs', 'value'), #tentativa
    Input(component_id='tempo', component_property='value'),
    Input(component_id='Cx0', component_property='value'),
    Input(component_id='Cs0', component_property='value'),
    Input(component_id='Cp0', component_property='value'),
    Input(component_id='V0', component_property='value')
)
def g(tab,tf, Cx0, Cs0, Cp0, V0):
    if (Cx0 == None) or (Cs0 == None) or (Cs0==None) or (Cp0== None) or (V0== None):
        fig = px.line()
        return fig
    else:
        t = np.linspace(0, tf, 1000)
        def g(y, t):
            Cx, Cs, Ce, V = y
            Mih = (Mimax * Cs / (Ks + Cs + (Cs ** 2) / Kis)) * (1 - Ce / Cemax) ** nc
            if t < tE:
                dydt = [(Mih - (F / V)) * Cx, (Csm - Cs) * (F / V) - ((1 / Yxs) * Cx * Mih),
                        Yes / Yxs * Cx * Mih - (F / V) * Ce, F]
            else:
                dydt = [(Mih - (0 / V)) * Cx, (Csm - Cs) * (0 / V) - ((1 / Yxs) * Cx * Mih),
                        Yes / Yxs * Cx * Mih - (0 / V) * Ce, 0]
            return dydt
        #Cx0 = 30.0  # Concentração inicial de células
        #Cs0 = 0  # Concentracao Inicial de Substrato
        #Cp0 = 0.0  # Concentracao Inicial de Produto
        #V0 = 0.6  # Volume Inicial (inóculo)
        y0 = [Cx0, Cs0, Cp0, V0]  # Vetor Condicoes Iniciais
        sol = odeint(g, y0, t)
        df = pd.DataFrame()
        df['tempo'] = pd.DataFrame(t)
        df['Concentração de células'] = pd.DataFrame(sol[:, 0])
        df['Concentração de substrato'] = pd.DataFrame(sol[:, 1])
        df['Concentração de Produto'] = pd.DataFrame(sol[:, 2])
        df['Volume'] = pd.DataFrame(sol[:, 3])
        if tab == 'tab-1':
            fig = px.line(df, x=df['tempo'],
                          y=[df['Concentração de células'], df['Concentração de substrato'], df['Concentração de Produto'],
                             df['Volume']], title='Batelada Alimentada')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
            )
            return fig
        if tab == 'tab-2':
            fig = px.line(df, x=df['tempo'], y= df['Concentração de células'], title= 'Concentração de Células')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
            )
            return fig
        if tab == 'tab-3':
            fig = px.line(df, x=df['tempo'], y= df['Concentração de substrato'], title= 'Concentração de Substrato')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
            )
            return fig
        if tab == 'tab-4':
            fig = px.line(df, x=df['tempo'], y= df['Concentração de Produto'], title= 'Concentração de Produto')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
            )
            return fig
        if tab == 'tab-5':
            fig = px.line(df, x=df['tempo'], y= df['Volume'], title= 'Volume')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
            )
            return fig



if __name__ == '__main__':
    app.run_server(debug=True)
