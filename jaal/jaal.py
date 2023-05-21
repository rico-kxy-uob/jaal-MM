# import
import dash
import visdcc
import pandas as pd
from dash import dcc, html
# import dash_core_components as dcc
# import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from .datasets.parse_dataframe import parse_dataframe
from .layout import get_app_layout, get_distinct_colors, create_color_legend, DEFAULT_COLOR, DEFAULT_NODE_SIZE, \
    DEFAULT_EDGE_SIZE

# class
class Jaal:
    """The main visualization class
    """

    def __init__(self, edge_df, node_df=None):
        """
        Parameters
        -------------
        edge_df: pandas dataframe
            The network edge data stored in format of pandas dataframe

        node_df: pandas dataframe (optional)
            The network node data stored in format of pandas dataframe
        """
        print("Parsing the data...", end="")
        self.data, self.scaling_vars = parse_dataframe(edge_df, node_df)
        self.filtered_data = self.data.copy()
        self.node_value_color_mapping = {}
        self.edge_value_color_mapping = {}
        print("Done")

    def _callback_search_graph(self, graph_data, search_text):
        """Only show the nodes which match the search text
        """
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        for node in nodes:
            if search_text in node['label']:
                node['hidden'] = False
            else:
                edges_node = []
                for edge in edges:
                    if str(node['idd']) in edge['idd']:
                        edges_node.append(edge)
                if len(edges_node) >= 1:
                    for edge in edges_node:
                        if search_text in edge['idd']:
                            node['hidden'] = False
                            break
                        else:
                            node['hidden'] = True
                else:
                    node['hidden'] = True
            # for edge in edges:
            #     if str(node['id']) in edge['id']:
            #         edges_node.append(edge)
            # for edge in edges_node:
            #     if search_text in node['label']:
            #         node['hidden'] = False
            #         break
            #     elif search_text in edge['id']:
            #         node['hidden'] = False
            #         break
            #     else:
            #         node['hidden'] = True
        graph_data['nodes'] = nodes
        return graph_data

    def _callback_filter_nodes(self, graph_data, filter_nodes_text):
        """Filter the nodes based on the Python query syntax
        """
        self.filtered_data = self.data.copy()
        node_df = pd.DataFrame(self.filtered_data['nodes'])
        try:
            node_list = node_df.query(filter_nodes_text)['id'].tolist()
            nodes = []
            for node in self.filtered_data['nodes']:
                if node['id'] in node_list:
                    nodes.append(node)
            self.filtered_data['nodes'] = nodes
            graph_data = self.filtered_data
        except:
            graph_data = self.data
            print("wrong node filter query!!")
        return graph_data

    def _callback_filter_edges(self, graph_data, filter_edges_text):
        """Filter the edges based on the Python query syntax
        """
        self.filtered_data = self.data.copy()
        edges_df = pd.DataFrame(self.filtered_data['edges'])
        try:
            edges_list = edges_df.query(filter_edges_text)['id'].tolist()
            edges = []
            for edge in self.filtered_data['edges']:
                if edge['id'] in edges_list:
                    edges.append(edge)
            self.filtered_data['edges'] = edges
            graph_data = self.filtered_data
        except:
            graph_data = self.data
            print("wrong edge filter query!!")
        return graph_data

    def _callback_edges_type(self, graph_data, edgestype_value):
        """Filter the edges based on the Python query syntax
        """
        self.filtered_data = self.data.copy()
        edges_df = pd.DataFrame(self.filtered_data['edges'])
        try:
            edges = []
            if 'LMLM' in edgestype_value:
                edges_list = edges_df.loc[edges_df['edgetype'] == 'LMLM']['id'].tolist()
                for edge in self.filtered_data['edges']:
                    if edge['id'] in edges_list:
                        edges.append(edge)

            if 'LMHC' in edgestype_value:
                edges_list = edges_df.loc[edges_df['edgetype'] == 'LMHC']['id'].tolist()
                for edge in self.filtered_data['edges']:
                    if edge['id'] in edges_list:
                        edges.append(edge)

            if 'HCHC' in edgestype_value:
                edges_list = edges_df.loc[edges_df['edgetype'] == 'HCHC']['id'].tolist()
                for edge in self.filtered_data['edges']:
                    if edge['id'] in edges_list:
                        edges.append(edge)

            self.filtered_data['edges'] = edges
            graph_data = self.filtered_data
        except:
            graph_data = self.data
            print("wrong edge type!!")
        return graph_data

    def _callback_omit_node_(self, graph_data, omit_node_value):
        """Filter the edges based on the Python query syntax
        """
        self.filtered_data = self.data.copy()
        edges_df = pd.DataFrame(graph_data['edges'])
        nodes_df = pd.DataFrame(self.filtered_data['nodes'])
        try:
            if len(omit_node_value) >= 1:
                nodes = []
                nodes_exist_list = list(set(list(edges_df['from']) + list(edges_df['to'])))
                for node in self.filtered_data['nodes']:
                    if node['id'] in nodes_exist_list:
                        nodes.append(node)
                self.filtered_data['nodes'] = nodes
                self.filtered_data['edges'] = graph_data['edges']
                graph_data = self.filtered_data
            else:
                graph_data = graph_data

        except:
            graph_data = self.data
            print("wrong omit node? !!")
        return graph_data

    def _callback_selfloop_omit_(self, graph_data, selfloop_omit):
        """Filter the edges based on the Python query syntax
        """
        self.filtered_data = self.data.copy()
        edges_df = pd.DataFrame(graph_data['edges'])
        nodes_df = pd.DataFrame(self.filtered_data['nodes'])
        try:
            if len(selfloop_omit)==1:
                edges_list = edges_df[edges_df['from'] != edges_df['to']]['id'].tolist()
                print('omit selfloop ok')
                edges = []
                for edge in self.filtered_data['edges']:
                    if edge['id'] in edges_list:
                        edges.append(edge)
                self.filtered_data['edges'] = edges
                graph_data = self.filtered_data
            else:
                graph_data = graph_data
        except:
            graph_data = self.data
            print("wrong omit selfloop!!")
        return graph_data

    def _callback_edges_sc_(self, graph_data, edgessc_value):
        """Filter the edges based on the Python query syntax
        """
        self.filtered_data = graph_data.copy()
        edges_df = pd.DataFrame(self.filtered_data['edges'])
        try:
            edges = []
            if 'Cross country edge' in edgessc_value:
                edges_list = edges_df.loc[edges_df['edge_sc'] == 'N']['id'].tolist()
                for edge in self.filtered_data['edges']:
                    if edge['id'] in edges_list:
                        edges.append(edge)

            if 'Domestic edge' in edgessc_value:
                edges_list = edges_df.loc[edges_df['edge_sc'] == 'Y']['id'].tolist()
                for edge in self.filtered_data['edges']:
                    if edge['id'] in edges_list:
                        edges.append(edge)
            self.filtered_data['edges'] = edges
            graph_data = self.filtered_data
        except:
            graph_data = self.data
            print("wrong edge across country? !!")
        return graph_data

    def _callback_year_range_(self, graph_data, year_range_value):
        """Filter the edges based on the Python query syntax
        """
        self.filtered_data = graph_data.copy()
        edges_df = pd.DataFrame(self.filtered_data['edges'])
        min_v = year_range_value[0] + 2002
        max_v = year_range_value[1] + 2002
        try:
            edges_df['year-factor'] = edges_df['year-factor'].astype(int)
            edges_list = edges_df.loc[( edges_df['year-factor'] >= min_v) &
                                      ( edges_df['year-factor'] <= max_v)]['id'].tolist()
            edges_df['year-factor'] = edges_df['year-factor'].astype(str)
            edges = []
            for edge in self.filtered_data['edges']:
                if edge['id'] in edges_list:
                    edges.append(edge)
            self.filtered_data['edges'] = edges
            print("year from " + str(min_v) + " to " + str(max_v))
            graph_data = self.filtered_data
        except:
            graph_data = self.data
            print("wrong year range !!")
        return graph_data

    def _callback_color_nodes(self, graph_data, color_nodes_value):
        value_color_mapping = {}
        # color option is None, revert back all changes
        self.data=graph_data
        if color_nodes_value == 'None':
            # revert to default color
            for node in self.data['nodes']:
                node['color'] = DEFAULT_COLOR
        else:
            print("inside color node", color_nodes_value)
            unique_values = pd.DataFrame(self.data['nodes'])[color_nodes_value].unique()
            colors = get_distinct_colors(len(unique_values))
            value_color_mapping = {x: y for x, y in zip(unique_values, colors)}
            for node in self.data['nodes']:
                node['color'] = value_color_mapping[node[color_nodes_value]]
        # filter the data currently shown
        filtered_nodes = [x['id'] for x in self.filtered_data['nodes']]
        self.filtered_data['nodes'] = [x for x in self.data['nodes'] if x['id'] in filtered_nodes]
        graph_data = self.filtered_data
        return graph_data, value_color_mapping

    def _callback_size_nodes(self, graph_data, size_nodes_value):
        self.data = graph_data
        # color option is None, revert back all changes
        if size_nodes_value == 'None':
            # revert to default color
            for node in self.data['nodes']:
                node['size'] = DEFAULT_NODE_SIZE
        else:
            print("Modifying node size using ", size_nodes_value)
            # fetch the scaling value
            minn = self.scaling_vars['node'][size_nodes_value]['min']
            maxx = self.scaling_vars['node'][size_nodes_value]['max']
            # define the scaling function
            scale_val = lambda x: 20 * (x - minn) / (maxx - minn)
            # set size after scaling
            for node in self.data['nodes']:
                node['size'] = node['size'] + scale_val(node[size_nodes_value])
        # filter the data currently shown
        filtered_nodes = [x['id'] for x in self.filtered_data['nodes']]
        self.filtered_data['nodes'] = [x for x in self.data['nodes'] if x['id'] in filtered_nodes]
        graph_data = self.filtered_data
        return graph_data

    def _callback_color_edges(self, graph_data, color_edges_value):
        value_color_mapping = {}
        # color option is None, revert back all changes
        self.data=graph_data
        if color_edges_value == 'None':
            # revert to default color
            for edge in self.data['edges']:
                edge['color']['color'] = DEFAULT_COLOR
        else:
            print("inside color edge", color_edges_value)
            unique_values = pd.DataFrame(self.data['edges'])[color_edges_value].unique()
            colors = get_distinct_colors(len(unique_values))
            value_color_mapping = {x: y for x, y in zip(unique_values, colors)}
            for edge in self.data['edges']:
                edge['color']['color'] = value_color_mapping[edge[color_edges_value]]
        # filter the data currently shown
        filtered_edges = [x['id'] for x in self.filtered_data['edges']]
        self.filtered_data['edges'] = [x for x in self.data['edges'] if x['id'] in filtered_edges]
        graph_data = self.filtered_data
        return graph_data, value_color_mapping

    def _callback_size_edges(self, graph_data, size_edges_value):
        # color option is None, revert back all changes
        self.data = graph_data
        if size_edges_value == 'None':
            # revert to default color
            for edge in self.data['edges']:
                edge['width'] = DEFAULT_EDGE_SIZE
        else:
            print("Modifying edge size using ", size_edges_value)
            # fetch the scaling value
            minn = self.scaling_vars['edge'][size_edges_value]['min']
            maxx = self.scaling_vars['edge'][size_edges_value]['max']
            # define the scaling function
            scale_val = lambda x: 20 * (x - minn) / (maxx - minn)
            # set the size after scaling
            for edge in self.data['edges']:
                edge['width'] = scale_val(edge[size_edges_value])
        # filter the data currently shown
        filtered_edges = [x['id'] for x in self.filtered_data['edges']]
        self.filtered_data['edges'] = [x for x in self.data['edges'] if x['id'] in filtered_edges]
        graph_data = self.filtered_data
        return graph_data

    def get_color_popover_legend_children(self, node_value_color_mapping={}, edge_value_color_mapping={}):
        """Get the popover legends for node and edge based on the color setting
        """
        # var
        popover_legend_children = []

        # common function
        def create_legends_for(title="Node", legends={}):
            # add title
            _popover_legend_children = [dbc.PopoverHeader(f"{title} legends")]
            # add values if present
            if len(legends) > 0:
                for key, value in legends.items():
                    _popover_legend_children.append(
                        # dbc.PopoverBody(f"Key: {key}, Value: {value}")
                        create_color_legend(key, value)
                    )
            else:  # otherwise add filler
                _popover_legend_children.append(dbc.PopoverBody(f"no {title.lower()} colored!"))
            #
            return _popover_legend_children

        # add node color legends
        popover_legend_children.extend(create_legends_for("Node", node_value_color_mapping))
        # add edge color legends
        popover_legend_children.extend(create_legends_for("Edge", edge_value_color_mapping))
        #
        return popover_legend_children

    def create(self, directed=False, vis_opts=None):
        """Create the Jaal app and return it

        Parameter
        ----------
            directed: boolean
                process the graph as directed graph?

            vis_opts: dict
                the visual options to be passed to the dash server (default: None)

        Returns
        -------
            app: dash.Dash
                the Jaal app
        """
        # create the app
        app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP,
                                              'https://cdnjs.cloudflare.com/ajax/libs/vis/4.20.1/vis.min.css'])

        # define layout
        app.layout = get_app_layout(self.data, color_legends=self.get_color_popover_legend_children(),
                                    directed=directed, vis_opts=vis_opts)

        # create callbacks to toggle legend popover
        @app.callback(
            Output("color-legend-popup", "is_open"),
            [Input("color-legend-toggle", "n_clicks")],
            [State("color-legend-popup", "is_open")],
        )
        def toggle_popover(n, is_open):
            if n:
                return not is_open
            return is_open

        # create callbacks to toggle hide/show sections - FILTER section
        @app.callback(
            Output("filter-show-toggle", "is_open"),
            [Input("filter-show-toggle-button", "n_clicks")],
            [State("filter-show-toggle", "is_open")],
        )
        def toggle_filter_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        # create callbacks to toggle hide/show sections - COLOR section
        @app.callback(
            Output("color-show-toggle", "is_open"),
            [Input("color-show-toggle-button", "n_clicks")],
            [State("color-show-toggle", "is_open")],
        )
        def toggle_filter_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        # create callbacks to toggle hide/show sections - COLOR section
        @app.callback(
            Output("size-show-toggle", "is_open"),
            [Input("size-show-toggle-button", "n_clicks")],
            [State("size-show-toggle", "is_open")],
        )
        def toggle_filter_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        # create the main callbacks
        @app.callback(
            [Output('graph', 'data'), Output('color-legend-popup', 'children')],
            [Input('search_graph', 'value'),
             Input('node_omit_input', 'value'),
             Input('selfloop_omit_input', 'value'),
             Input('edgestype_input', 'value'),
             Input('edges_sc_input', 'value'),
             Input('filter_nodes', 'value'),
             Input('filter_edges', 'value'),
             Input('color_nodes', 'value'),
             Input('color_edges', 'value'),
             Input('size_nodes', 'value'),
             Input('size_edges', 'value'),
             Input('year_range', 'value')],
            [State('graph', 'data')]
        )
        def setting_pane_callback(search_text, omit_node_value, selfloop_value, edgestype_value,
                                  edgessc_value, filter_nodes_text, filter_edges_text, color_nodes_value,
                                  color_edges_value, size_nodes_value, size_edges_value,
                                  year_range_value, graph_data):
            # fetch the id of option which triggered
            ctx = dash.callback_context
            # if its the first call
            if not ctx.triggered:
                print("No trigger")
                return [self.data, self.get_color_popover_legend_children()]
            else:
                # find the id of the option which was triggered
                input_id = ctx.triggered[0]['prop_id'].split('.')[0]

                if len(edgestype_value) <= 3:
                    graph_data = self._callback_edges_type(graph_data, edgestype_value)
                if len(edgessc_value) <= 2:
                    graph_data = self._callback_edges_sc_(graph_data, edgessc_value)
                # perform operation in case of search graph option
                if input_id == "search_graph":
                    graph_data = self._callback_search_graph(graph_data, search_text)
                # In case filter nodes was triggered
                if input_id == 'filter_nodes':
                    graph_data = self._callback_filter_nodes(graph_data, filter_nodes_text)
                # In case filter edges was triggered
                if input_id == 'filter_edges':
                    graph_data = self._callback_filter_edges(graph_data, filter_edges_text)
                # If color node text is provided
                if input_id == 'color_nodes':
                    graph_data, self.node_value_color_mapping = self._callback_color_nodes(graph_data,
                                                                                           color_nodes_value)
                # If color edge text is provided
                if input_id == 'color_edges':
                    graph_data, self.edge_value_color_mapping = self._callback_color_edges(graph_data,
                                                                                           color_edges_value)
                # If size node text is provided
                if input_id == 'size_nodes':
                    graph_data = self._callback_size_nodes(graph_data, size_nodes_value)
                # If size edge text is provided
                if input_id == 'size_edges':
                    graph_data = self._callback_size_edges(graph_data, size_edges_value)
                if selfloop_value is not None:
                    graph_data = self._callback_selfloop_omit_(graph_data, selfloop_value)
                if (year_range_value[1]-year_range_value[0])!=20:
                    graph_data = self._callback_year_range_(graph_data, year_range_value)

                if omit_node_value is not None:
                    graph_data = self._callback_omit_node_(graph_data, omit_node_value)



            # create the color legend childrens
            color_popover_legend_children = self.get_color_popover_legend_children(self.node_value_color_mapping,
                                                                                   self.edge_value_color_mapping)
            # finally return the modified data
            return [graph_data, color_popover_legend_children]

        # return server
        return app

    def plot(self, debug=False, host="127.0.0.2", port="8060", directed=False, vis_opts=None):
        """Plot the Jaal by first creating the app and then hosting it on default server

        Parameter
        ----------
            debug (boolean)
                run the debug instance of Dash?

            host: string
                ip address on which to run the dash server (default: 127.0.0.1)

            port: string
                port on which to expose the dash server (default: 8050)

            directed (boolean):
                whether the graph is directed or not (default: False)

            vis_opts: dict
                the visual options to be passed to the dash server (default: None)
        """
        # call the create_graph function
        app = self.create(directed=directed, vis_opts=vis_opts)
        # run the server
        app.run_server(debug=debug, host=host, port=port)