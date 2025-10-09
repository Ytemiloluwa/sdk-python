def t_sort(edges):
    """
    Perform a topological sort on directed graph edges.
    Returns a list of nodes in topological order.
    """
    # Create a graph representation
    graph = {}
    nodes = set()

    # Add all nodes and edges to the graph
    for edge in edges:
        from_node, to_node = edge
        nodes.add(from_node)
        nodes.add(to_node)

        if from_node not in graph:
            graph[from_node] = []
        graph[from_node].append(to_node)

    # Initialize all nodes in the graph
    for node in nodes:
        if node not in graph:
            graph[node] = []

    # Track visited nodes and result
    visited = set()
    temp_visited = set()
    result = []

    def visit(node):
        if node in temp_visited:
            raise ValueError(f"Cyclic dependency detected involving {node}")
        if node in visited:
            return

        temp_visited.add(node)

        for neighbor in graph.get(node, []):
            visit(neighbor)

        temp_visited.remove(node)
        visited.add(node)
        result.append(node)

    # Visit all nodes
    for node in nodes:
        if node not in visited:
            visit(node)

    return result
