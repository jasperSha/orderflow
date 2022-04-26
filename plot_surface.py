import plotly.graph_objects as go

def plot_surface(df, S):
    '''
    y = strike
    x = expiration date (days to expiry, reversed?)
    z = gamma * open interest

    '''
    S = float(S)
    gamma = (df['gamma'] * df['open_interest']).values
    plot_gamma = []
    for g in gamma:
        print(type(g), type(S))
        print(g, S)
        gam = g * S * S
        plot_gamma.append(gam)
    gamma = plot_gamma
    dates = df['expiry_date'].values
    strikes = df['strike'].values
    fig = go.Figure(data=[go.Surface(z=gamma, x=dates, y=strikes)])
    fig.update_layout(
        title='gamma surface',
        autosize=True,
        width=500,
        height=500,
        margin=dict(l=65, r=50, b=65, t=90)
    )
    fig.show()