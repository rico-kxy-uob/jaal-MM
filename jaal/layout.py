"""
Layout code for the application
"""
# Import
#---------
import os
import visdcc
import base64
import pandas as pd
from dash import dcc, html
# import dash_core_components as dcc
# import dash_html_components as html
import dash_bootstrap_components as dbc
import jaal

# Constants
#--------------
# default node and edge size
DEFAULT_NODE_SIZE = 7
DEFAULT_EDGE_SIZE = 1

# default node and egde color
DEFAULT_COLOR = '#97C2FC'

 # Taken from https://stackoverflow.com/questions/470690/how-to-automatically-generate-n-distinct-colors
KELLY_COLORS_HEX = [
    "#FF4A46", "#008941", "#006FA6", "#1CE6FF", "#FFFF00", "#FF34FF", "#A30059",
    "#FFDBE5", "#7A4900", "#0000A6", "#63FFAC", "#B79762", "#004D43", "#8FB0FF", "#997D87",
    "#5A0007", "#809693", "#FEFFE6", "#1B4400", "#4FC601", "#3B5DFF", "#4A3B53", "#FF2F80",
    "#61615A", "#BA0900", "#6B7900", "#00C2A0", "#FFAA92", "#FF90C9", "#B903AA", "#D16100",
    "#DDEFFF", "#000035", "#7B4F4B", "#A1C299", "#300018", "#0AA6D8", "#013349", "#00846F",
    "#372101", "#FFB500", "#C2FFED", "#A079BF", "#CC0744", "#C0B9B2", "#C2FF99", "#001E09",
    "#00489C", "#6F0062", "#0CBD66", "#EEC3FF", "#456D75", "#B77B68", "#7A87A1", "#788D66",
    "#885578", "#FAD09F", "#FF8A9A", "#D157A0", "#BEC459", "#456648", "#0086ED", "#886F4C",

    "#34362D", "#B4A8BD", "#00A6AA", "#452C2C", "#636375", "#A3C8C9", "#FF913F", "#938A81",
    "#575329", "#00FECF", "#B05B6F", "#8CD0FF", "#3B9700", "#04F757", "#C8A1A1", "#1E6E00",
    "#7900D7", "#A77500", "#6367A9", "#A05837", "#6B002C", "#772600", "#D790FF", "#9B9700",
    "#549E79", "#FFF69F", "#201625", "#72418F", "#BC23FF", "#99ADC0", "#3A2465", "#922329",
    "#5B4534", "#FDE8DC", "#404E55", "#0089A3", "#CB7E98", "#A4E804", "#324E72", "#6A3A4C",
    "#83AB58", "#001C1E", "#D1F7CE", "#004B28", "#C8D0F6", "#A3A489", "#806C66", "#222800",
    "#BF5650", "#E83000", "#66796D", "#DA007C", "#FF1A59", "#8ADBB4", "#1E0200", "#5B4E51",
    "#C895C5", "#320033", "#FF6832", "#66E1D3", "#CFCDAC", "#D0AC94", "#7ED379", "#012C58"
    # "#FFB300", # Vivid Yellow
    # "#803E75", # Strong Purple
    # "#FF6800", # Vivid Orange
    # "#A6BDD7", # Very Light Blue
    # "#C10020", # Vivid Red
    # "#CEA262", # Grayish Yellow
    # "#817066", # Medium Gray
    #
    # # The following don't work well for people with defective color vision
    # "#007D34", # Vivid Green
    # "#F6768E", # Strong Purplish Pink
    # "#00538A", # Strong Blue
    # "#FF7A5C", # Strong Yellowish Pink
    # "#53377A", # Strong Violet
    # "#FF8E00", # Vivid Orange Yellow
    # "#B32851", # Strong Purplish Red
    # "#F4C800", # Vivid Greenish Yellow
    # "#7F180D", # Strong Reddish Brown
    # "#93AA00", # Vivid Yellowish Green
    # "#593315", # Deep Yellowish Brown
    # "#F13A13", # Vivid Reddish Orange
    # "#232C16", # Dark Olive Green
    ]

DEFAULT_OPTIONS = {
    'height': '600px',
    'width': '100%',
    'interaction':{'hover': True},
    # 'edges': {'scaling': {'min': 1, 'max': 5}},
    'physics':{'stabilization':{'iterations': 100}}
}

# Code
#---------
def get_options(directed, opts_args):
    opts = DEFAULT_OPTIONS.copy()
    opts['edges'] = { 'arrows': { 'to': directed } }
    if opts_args is not None:
        opts.update(opts_args)
    return opts

def get_distinct_colors(n):
    """Return distict colors, currently atmost 20

    Parameters
    -----------
    n: int
        the distinct colors required
    """
    if n <= 2:
        return KELLY_COLORS_HEX[3:5]
    elif n <= 100:
        return KELLY_COLORS_HEX[:n]

def create_card(id, value, description):
    """Creates card for high level stats

    Parameters
    ---------------
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4(id=id, children=value, className='card-title'),
                html.P(children=description),
            ]))

def create_color_legend(text, color):
    """Individual row for the color legend
    """
    return create_row([
        html.Div(style={'width': '10px', 'height': '10px', 'background-color': color}),
        html.Div(text, style={'padding-left': '10px'}),
    ])

def fetch_flex_row_style():
    return {'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 'align-items': 'center'}

def create_row(children, style=fetch_flex_row_style()):
    return dbc.Row(children,
                   style=style,
                   className="column flex-display")

search_form = dbc.FormGroup(
    [
        # dbc.Label("Search", html_for="search_graph"),
        dbc.Input(type="search", id="search_graph", placeholder="Search node in graph..."),
        dbc.FormText(
            "Show the node you are looking for",
            color="secondary",
        ),
    ]
)

filter_node_form = dbc.FormGroup([
    # dbc.Label("Filter nodes", html_for="filter_nodes"),
    dbc.Textarea(id="filter_nodes", placeholder="Enter filter node query here..."),
    dbc.FormText(
        html.P([
            "Filter on nodes properties by using ",
            html.A("Pandas Query syntax",
            href="https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html"),
        ]),
        color="secondary",
    ),
])

filter_edge_form = dbc.FormGroup([
    # dbc.Label("Filter edges", html_for="filter_edges"),
    dbc.Textarea(id="filter_edges", placeholder="Enter filter edge query here..."),
    dbc.FormText(
        html.P([
            "Filter on edges properties by using ",
            html.A("Pandas Query syntax",
            href="https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html"),
        ]),
        color="secondary",
    ),
])

def get_select_form_layout(id, options, label, description):
    """Creates a select (dropdown) form with provides details

    Parameters
    -----------
    id: str
        id of the form
    options: list
        options to show
    label: str
        label of the select dropdown bar
    description: str
        long text detail of the setting
    """
    return  dbc.FormGroup([
                dbc.InputGroup([
                    dbc.InputGroupAddon(label, addon_type="append"),
                    dbc.Select(id=id,
                        options=options
                    ),]),
                dbc.FormText(description, color="secondary",)
            ,])

def get_categorical_features(df_, unique_limit=100, blacklist_features=['shape', 'label', 'id']):
    """Identify categorical features for edge or node data and return their names
    Additional logics: (1) cardinality should be within `unique_limit`, (2) remove blacklist_features
    """
    # identify the rel cols + None
    cat_features = ['None'] + df_.columns[(df_.dtypes == 'object') & (df_.apply(pd.Series.nunique) <= unique_limit)].tolist()
    # remove irrelevant cols
    try:
        for col in blacklist_features:
            cat_features.remove(col)
    except:
        pass
    # return
    return cat_features

def get_numerical_features(df_, unique_limit=100):
    """Identify numerical features for edge or node data and return their names
    """
    # supported numerical cols
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    # identify numerical features
    numeric_features = ['None'] + df_.select_dtypes(include=numerics).columns.tolist()
    # remove blacklist cols (for nodes)
    try:
        numeric_features.remove('size')
    except:
        pass
    # return
    return numeric_features

def get_app_layout(graph_data, color_legends=[], directed=False, vis_opts=None):

    # """Create and return the layout of the app
    #
    # Parameters
    # --------------
    # graph_data: dict{nodes, edges}
    #     network data in format of visdcc
    # """
    # Step 1-2: find categorical features of nodes and edges
    cat_node_features = get_categorical_features(pd.DataFrame(graph_data['nodes']), 100, ['shape', 'label', 'id'])
    cat_edge_features = get_categorical_features(pd.DataFrame(graph_data['edges']).drop(columns=['color']), 100, ['color', 'from', 'to', 'id','year'])
    # Step 3-4: Get numerical features of nodes and edges
    num_node_features = get_numerical_features(pd.DataFrame(graph_data['nodes']))
    num_edge_features = get_numerical_features(pd.DataFrame(graph_data['edges']))
    # Step 5: create and return the layout
    # resolve path
    this_dir, _ = os.path.split(__file__)
    image_filename = os.path.join(this_dir, "assest", "logo.png")
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    return html.Div([
            create_row(html.H2(children="Multiple myeloma in the Sub-Saharan")), # Title
            dcc.RangeSlider(0, 20, 1,
                       value=[0,20],
                       marks={
                           0: '2002',
                           2: '2004',
                           4: '2006',
                           6: '2008',
                           8: '2010',
                           10: '2012',
                           12: '2014',
                           14: '2016',
                           16: '2018',
                           18: '2020',
                           20: '2022',
                       },
                       id='year_range'
            ),
            # create_row(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), width="80px")),
            create_row([
                dbc.Col([
                    # setting panel
                    dbc.Form([
                        dbc.Checklist(
                            id='node_omit_input',
                            inline=True,
                            options=[
                                {'label': item, 'value': item}
                                for item in ['Omit isolated node']
                            ],
                            style={
                                'width': '300px'
                            }
                        ),
                        # ---- search section ----
                        html.H6("Search"),
                        html.Hr(className="my-2"),
                        search_form,
                        # ---- filter section ----
                        create_row([
                            html.H6("Filter"),
                            dbc.Button("Hide/Show", id="filter-show-toggle-button", outline=True, color="secondary", size="sm"), # legend
                        ], {**fetch_flex_row_style(), 'margin-left': 0, 'margin-right':0, 'justify-content': 'space-between'}),
                        dbc.Collapse([
                            html.Hr(className="my-2"),
                            filter_node_form,
                            filter_edge_form,
                        ], id="filter-show-toggle", is_open=False),

                        dbc.Checklist(
                            id='selfloop_omit_input',
                            inline=True,
                            options=[
                                {'label': item,'value':item}
                                for item in ['Omit self-loop']
                            ],
                            style={
                                'width': '300px'
                            }
                        ),

                        html.H6("Edge type"),
                        dbc.Checklist(
                            id='edgestype_input',
                            inline=True,
                            options=[
                                {'label': item, 'value': item}
                                for item in ['LMLM','LMHC','HCHC']
                            ],
                            value=['LMLM','LMHC','HCHC'],
                            style={
                                'width': '300px'
                            }
                        ),
                        html.H6(" "),
                        dbc.Checklist(
                            id='edges_sc_input',
                            inline=True,
                            options=[
                                {'label': item, 'value': item}
                                for item in ['Cross country edge','Domestic edge']
                            ],
                            value=['Cross country edge','Domestic edge'],
                            style={
                                'width': '300px'
                            }
                        ),


                        # ---- color section ----
                        create_row([
                            html.H6("Color"), # heading
                            html.Div([
                                dbc.Button("Hide/Show", id="color-show-toggle-button", outline=True, color="secondary", size="sm"), # legend
                                dbc.Button("Legends", id="color-legend-toggle", outline=True, color="secondary", size="sm"), # legend
                            ]),
                            # add the legends popup
                            dbc.Popover(
                                children=color_legends,
                                id="color-legend-popup", is_open=False, target="color-legend-toggle",
                            ),
                        ], {**fetch_flex_row_style(), 'margin-left': 0, 'margin-right':0, 'justify-content': 'space-between'}),
                        dbc.Collapse([
                            html.Hr(className="my-2"),
                            get_select_form_layout(
                                id='color_nodes',
                                options=[{'label': opt, 'value': opt} for opt in cat_node_features],
                                label='Color nodes by',
                                description='Select the categorical node property to color nodes by'
                            ),
                            get_select_form_layout(
                                id='color_edges',
                                options=[{'label': opt, 'value': opt} for opt in cat_edge_features],
                                label='Color edges by',
                                description='Select the categorical edge property to color edges by'
                            ),
                        ], id="color-show-toggle", is_open=False),

                        # ---- size section ----
                        create_row([
                            html.H6("Size"), # heading
                            dbc.Button("Hide/Show", id="size-show-toggle-button", outline=True, color="secondary", size="sm"), # legend
                            # dbc.Button("Legends", id="color-legend-toggle", outline=True, color="secondary", size="sm"), # legend
                            # add the legends popup
                            # dbc.Popover(
                            #     children=color_legends,
                            #     id="color-legend-popup", is_open=False, target="color-legend-toggle",
                            # ),
                        ], {**fetch_flex_row_style(), 'margin-left': 0, 'margin-right':0, 'justify-content': 'space-between'}),
                        dbc.Collapse([
                            html.Hr(className="my-2"),
                            get_select_form_layout(
                                id='size_nodes',
                                options=[{'label': opt, 'value': opt} for opt in num_node_features],
                                label='Size nodes by',
                                description='Select the numerical node property to size nodes by'
                            ),
                            get_select_form_layout(
                                id='size_edges',
                                options=[{'label': opt, 'value': opt} for opt in num_edge_features],
                                label='Size edges by',
                                description='Select the numerical edge property to size edges by'
                            ),
                        ], id="size-show-toggle", is_open=False),

                    ], className="card", style={'padding': '5px', 'background': '#e5e5e5'}),
                ],width=3, style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
                # graph
                dbc.Col(
                    visdcc.Network(
                        id = 'graph',
                        data = graph_data,
                        options = get_options(directed,vis_opts)
                    ),
                        width=9,

            )])
    ])
