"""
Parse network data from dataframe format into visdcc format
"""
import random
import visdcc
import networkx
import textwrap
import math

def compute_scaling_vars_for_numerical_cols(df):
    """Identify and scale numerical cols"""
    # identify numerical cols
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    numeric_cols = df.select_dtypes(include=numerics).columns.tolist()
    # var to hold the scaling function
    scaling_vars = {}
    # scale numerical cols
    for col in numeric_cols:
        minn, maxx = df[col].min(), df[col].max()
        scaling_vars[col] = {'min': minn, 'max': maxx}
    # return
    return scaling_vars

def parse_dataframe(edge_df, node_df=None):
    """Parse the network dataframe into visdcc format

    Parameters
    -------------
    edge_df: pandas dataframe
            The network edge data stored in format of pandas dataframe

    node_df: pandas dataframe (optional)
            The network node data stored in format of pandas dataframe
    """
    # Data checks
    # Check 1: mandatory columns presence
    if ('from' not in edge_df.columns) or ('to' not in edge_df.columns):
        raise Exception("Edge dataframe missing either 'from' or 'to' column.")
    # Check 2: if node_df is present, it should contain 'node' column
    if node_df is not None:
        if 'id' not in node_df.columns:
            raise Exception("Node dataframe missing 'id' column.")

    # Data post processing - convert the from and to columns in edge data as string for searching
    edge_df.loc[:, ['from', 'to']] = edge_df.loc[:, ['from', 'to']].astype(str)

    # Data pot processing (scaling numerical cols in nodes and edge)
    scaling_vars = {'node': None, 'edge': None}
    if node_df is not None:
        scaling_vars['node'] = compute_scaling_vars_for_numerical_cols(node_df)
    scaling_vars['edge'] = compute_scaling_vars_for_numerical_cols(edge_df)

    # create node list w.r.t. the presence of absence of node_df
    nodes = []
    if node_df is None:
        node_list = list(set(edge_df['from'].unique().tolist() + edge_df['to'].unique().tolist()))
        nodes = [{'id': node_name,'shape': 'dot', 'size': 7} for node_name in node_list]
    else:
        # convert the node id column to string
        node_df.loc[:, 'id'] = node_df.loc[:, 'id'].astype(str)
        node_df.loc[:, 'idd'] = node_df.loc[:, 'Country'].astype(str)+':'+\
                               node_df.loc[:, 'City'].astype(str)+':'+\
                               node_df.loc[:, 'id'].astype(str)
        # create the node data
        for node in node_df.to_dict(orient='records'):
            ll=len(str(node['au_list']).split(','))
            if ll>=8:
                rown=int(ll/5)+1
                nodetitle=textwrap.wrap(str(node['au_list']),80)
                nodetitle='<br>'.join(nodetitle)

                if node['Country_type']=='LMIC':
                    nodes.append({**node, **{'label': node['idd'],
                                             'title': str(node['pmid_list'])+'<br>'+nodetitle,
                                             'shape': 'square', 'size': 7}})
                else:
                    nodes.append({**node, **{'label': node['idd'],
                                             'title': str(node['pmid_list'])+'<br>'+nodetitle,
                                             'shape': 'dot', 'size': 7}})
            else:
                if node['Country_type']=='LMIC':
                    nodes.append({**node, **{'label': node['idd'],
                                             'title':str(node['pmid_list'])+'<br>'+str(node['au_list']),
                                             'shape': 'square', 'size': 7}})
                else:
                    nodes.append({**node, **{'label': node['idd'],
                                             'title': str(node['pmid_list']) + '<br>' + str(node['au_list']),
                                             'shape': 'dot', 'size': 7}})

    # create edges from df
    edges = []
    edge_df.loc[:, 'year-factor'] = edge_df.loc[:, 'year-factor'].astype(str)
    for row in edge_df.to_dict(orient='records'):
        edges.append({**row,
                      **{'id':row['from']+"__" +row['to']+'/'+str(row['year-factor']),
                         'idd':node_df.loc[node_df[node_df['id']==row['from']].index[0],'idd']+ \
                               "--" +\
                               node_df.loc[node_df[node_df['id']==row['to']].index[0],'idd']+"/"+str(row['year-factor']),
                         'title': str(row['from'])+"__" +str(row['to'])+'/'+str(row['year-factor']),
                         'year-factor':str(row['year-factor']),
                         'color': {'color': '#97C2FC'},
                         "selfReferenceSize": math.log((int(row['year-factor'])-2001)/0.2,1.2)
                         }
                      })
        # edges.append({**row, **{'id': row['from'] + "__" + row['to'],  'color': {'color': '#97C2FC'}}})

    # return
    return {'nodes': nodes, 'edges': edges}, scaling_vars