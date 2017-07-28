import graphviz as gv

"""###############
   # GRAPH Styles
   ##################"""

styles = {
    'graph': {
        'label': 'A Fancy Graph',
        'fontsize': '16',
        'fontcolor': 'white',
        'bgcolor': '#333333',
        'rankdir': 'LR',
    },
    'nodes': {
        'fontname': 'Helvetica',
        'shape': 'Mrecord',
        'fontcolor': 'white',
        'color': 'white',
        'style': 'filled',
        'fillcolor': '#006699',
    },
    'edges': {
        'style': 'dashed',
        'color': 'white',
        'arrowhead': 'open',
        'fontname': 'Courier',
        'fontsize': '12',
        'fontcolor': 'white',
    }
}

"""###############
   # HELPER FUNCTIONS
   ##################"""

# Create nodes from a models_list
# =========================
def create_nodes(graph, models_list):
    for model in models_list:
        fields_str = model.name + "|"
        fields_str += "".join([substr + "|" for substr in model.fields])
        fields_str += "".join([substr + "|" for substr in model.reference_fields])
        graph.node(model.name, fields_str)
    return graph

# Create edges from a models_list
# =========================
def create_edges(graph, models_list):
    for model in models_list:
        now = model.name
        for ref in model.reference_fields:
            graph.edge(now, ref)
    return graph


# Apply the styles
# =========================
def apply_styles(graph, styles):
    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )
    return graph


"""###############
   # MAIN OUTPUT FUNCTION
   ##################"""

def create_digraph_for_models(models_list):
    g1 = gv.Digraph(format='svg', engine="dot")
    apply_styles(g1, styles)
    g1 = create_nodes(g1, models_list)
    g1 = create_edges(g1, models_list)
    return g1.render('./output_graph')


"""###############
   # TXT OUTPUT FUNCTION
   ##################"""

def print_to_output(models_list):
    with open('./graph.txt', 'w') as f:
        write = f.write
        for model in models_list:
            write(model.name + "\n--\n\n")
            for field in model.reference_fields:
                write("* " + field + ": ReferenceField"  + "\n")
            for field in model.fields:
                write("+ " + field + "\n")
            write("-----------------------------------------------------\n")
    print("RENDERING DONE!")
