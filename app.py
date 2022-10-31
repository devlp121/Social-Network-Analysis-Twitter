from dash import dcc, html, dash_table, Dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output, State
import dash_auth
import plotly.express as px

import pandas as pd
import json
import igraph as ig


cyto.load_extra_layouts()

app = Dash(__name__, external_stylesheets=[
           dbc.themes.BOOTSTRAP])


# Create server variable with Flask server object for use with gunicorn
server = app.server

main_attr = "worldcup"


def dash_tbl(df):
    tbl = dash_table.DataTable(
        df.to_dict('records'),
        [{"name": i, "id": i} for i in df.columns],
        page_size=20,  # we have less data in this example, so setting to 20
        style_table={
            'height': '200px',
            'overflowY': 'auto',
            'textAlign': 'left'})
    return tbl


def cyto_interaction(elements):
    fig = cyto.Cytoscape(
        id="core_19_cytoscape",
        layout={"name": "cola"},
        style={"width": "100%", "height": "400px"},
        elements=elements,
    )

    return fig


def list_to_df(lst):
    cent_df = pd.DataFrame(lst, columns=["Name", "Centrality"])
    dff = cent_df.to_dict('records')
    return dff


with open(f"export/{main_attr}/lda_topics.json", "r") as f:
    lda_topics = json.load(f)
topics_txt = [lda_topics[str(i)] for i in range(len(lda_topics))]
topics_txt = [[j.split("*")[1].replace('"', "")
               for j in i] for i in topics_txt]
topics_txt = ["; ".join(i) for i in topics_txt]

col_swatch = px.colors.qualitative.Dark24

topics_html = list()
for topic_html in [
    html.Span([str(i) + ": " + topics_txt[i]], style={"color": col_swatch[i]})
    for i in range(len(topics_txt))
]:
    topics_html.append(topic_html)
    topics_html.append(html.Br())


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink(
                "Review",
                href="",
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Source Data",
                href="",
            )
        ),
    ],
    brand="Vorel Report on Social Network Analysis",
    brand_href="#",
    color="dark",
    dark=True,
)

body_layout = dbc.Container(
    [
        dbc.Row(
            [
                dcc.Markdown(
                    f"""
            ## Social Network Analysis


            -----
            """
                ),
                dcc.Markdown(
                    f"""
            #### Interaction Analysis
            Interaction types are analyzed based on tweet mentions, quotes, retweets and replies.
            
            -----
            """
                ),
                dbc.Label('Select Interaction Type'),
                dcc.Dropdown(
                    id='dropdown-update-interaction',
                    clearable=False,
                    options=[
                        {'label': 'Mention', 'value': 'mention'},
                        {'label': 'Retweet', 'value': 'retweet'},
                        {'label': 'Reply', 'value': 'reply'},
                        {'label': 'Quote', 'value': 'quote'},
                    ],
                    value='mention'
                ),
                # html.Div(id='output-container-1'),
                dcc.Markdown(
                    f"""
                    In-degree measures of a node indicate the connections from other nodes towards it.
                    
                    Out-degree refers to directed connections from a node.

                    
                    -----
                    """
                ),
                dbc.Col(
                    dbc.Container([
                        dbc.Label('In-Degree Measures'),
                        dash_table.DataTable(
                            id='tblin',
                            page_size=20,  # we have less data in this example, so setting to 20
                            style_table={
                                'height': '200px',
                                'overflowY': 'auto',
                                'textAlign': 'left'
                            },
                            style_cell={
                                'textAlign': 'left',
                            }),
                        dbc.Alert(id='tbl_in'),
                    ])
                ), dbc.Col(
                    dbc.Container([
                        dbc.Label('Out-Degree Measures'),
                        dash_table.DataTable(
                            id='tblout',
                            page_size=20,  # we have less data in this example, so setting to 20
                            style_table={
                                'height': '200px',
                                'overflowY': 'auto',
                                'textAlign': 'left'
                            },
                            style_cell={'textAlign': 'left'}),
                        dbc.Alert(id='tbl_out'),
                    ])
                ),

            ]
        ),
        dbc.Row(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    "Select the layout of the network graph",
                                    className="mr-1",
                                ),
                                dcc.Dropdown(
                                    id='dropdown-update-layout',
                                    value='cose',
                                    clearable=False,
                                    options=[
                                        {'label': name.capitalize(), 'value': name}
                                        for name in ['cose', 'grid', 'random', 'circle', 'cola', 'concentric']
                                    ]
                                ),
                            ],
                            sm=12,
                            md=5,

                        ),

                    ]
                ),
                dbc.Row(
                    [
                        cyto.Cytoscape(
                            id="core_19_cytoscape",
                            layout={"name": "cola"},
                            style={"width": "100%", "height": "700px"},
                        )
                    ]
                )


            ]
        ),
        dbc.Row(
            [
                dcc.Markdown(
                    f"""
            -----

            #### Topic Modelling - LDA Analysis
            Organizing tweets based on salient topics that are prevalent.
            
            -----
            """
                ),
                dbc.Container([
                    dbc.Label('Topics'),

                ]),
                html.Div(
                    topics_html,
                    style={
                        "fontSize": 15,
                        "height": "300px",
                        "overflow": "auto",
                        "margin-bottom": "24px"
                    },
                ),


            ]
        ),
        dbc.Row(
            [
                dcc.Markdown(
                    """
            \* 'The data is retrieved from Twitter Platform
            """
                )
            ],
            style={"fontSize": 13, "color": "gray"},
        ),

    ],
    style={"marginTop": 20},
)

app.layout = html.Div([navbar, body_layout])


@app.callback(Output('core_19_cytoscape', 'layout'),
              Input('dropdown-update-layout', 'value'))
def update_layout(layout):
    return {
        'name': layout,
        'animate': True
    }


@app.callback(
    Output('output-container-1', 'children'),
    Input('dropdown-update-interaction', 'value'))
def update_testing(value):
    print(value)
    return f'The value is {value}'


# @app.callback(
#     Output('intermediate-value', 'data'),
#     Input('dropdown-update-interaction', 'value'))
# def update_interaction(value):
#     url = 'export/{}.gml'.format(value)
#     graph = ig.Graph.Read_GML(url)

#     return {
#         'name': graph,
#         'data': graph
#     }


@app.callback(
    Output('core_19_cytoscape', 'elements'),
    Input('dropdown-update-interaction', 'value'))
def update_net_graph(value):
    url = f'export/{main_attr}/{value}.gml'
    data = ig.Graph.Read_GML(url)
    labels = list(data.vs['screenname'])
    id = list(data.vs['id'])

    id = [int(x) for x in id]
    id = [str(x) for x in id]

    nodes_name = zip(id, labels)

    E = [e.tuple for e in data.es]
    E = [tuple(map(str, tup)) for tup in E]

    nodes = [
        {
            'data': {'id': short, 'label': label}
        }
        for short, label in nodes_name
    ]

    edges = [
        {'data': {'source': source, 'target': target}}
        for source, target in E
    ]

    elements = nodes + edges
    return elements


@app.callback(
    Output('tblin', 'data'),
    Input('dropdown-update-interaction', 'value'))
def update_tblin(value):
    url = f'export/{main_attr}/{value}.gml'
    data = ig.Graph.Read_GML(url)
    labels = list(data.vs['screenname'])
    _inlist = data.indegree()

    inlist = list(zip(labels, _inlist))
    inlist.sort(key=lambda i: i[1], reverse=True)

    df_in = list_to_df(inlist)

    return df_in


@app.callback(
    Output('tblout', 'data'),
    Input('dropdown-update-interaction', 'value'))
def update_tblout(value):
    url = f'export/{main_attr}/{value}.gml'
    data = ig.Graph.Read_GML(url)
    labels = list(data.vs['screenname'])

    _outlist = data.outdegree()

    outlist = list(zip(labels, _outlist))
    outlist.sort(key=lambda i: i[1], reverse=True)

    df_out = list_to_df(outlist)

    return df_out


if __name__ == '__main__':
    app.run_server(debug=True)
