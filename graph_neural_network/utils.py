import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random

def network_viz(data, num_nodes=80):
    """
    Create a simple, clear network visualization
    """
    
    # Convert to NetworkX
    edge_list = data.edge_index.t().numpy()
    G_full = nx.Graph()
    G_full.add_edges_from(edge_list)
    
    # Find a good starting point - not the super-hub, but a moderately connected node
    degrees = dict(G_full.degree())
    
    # Get nodes with "moderate" degrees (not too high, not too low)
    moderate_nodes = [node for node, deg in degrees.items() if 20 <= deg <= 100]
    start_node = random.choice(moderate_nodes)
    
    # Expand from this node to get a diverse neighborhood
    visited = {start_node}
    queue = [start_node]
    
    while queue and len(visited) < num_nodes:
        current = queue.pop(0)
        neighbors = list(G_full.neighbors(current))
        random.shuffle(neighbors)  # Add randomness for diversity
        
        for neighbor in neighbors:
            if neighbor not in visited and len(visited) < num_nodes:
                visited.add(neighbor)
                queue.append(neighbor)
    
    # Create subgraph
    G_sub = G_full.subgraph(visited).copy()
    sub_degrees = dict(G_sub.degree())
    
    # Simple classification: high-degree = "popular pages", low-degree = "regular pages"
    degree_threshold = np.percentile(list(sub_degrees.values()), 70)  # Top 30%
    
    popular_pages = [node for node in G_sub.nodes() if sub_degrees[node] >= degree_threshold]
    regular_pages = [node for node in G_sub.nodes() if sub_degrees[node] < degree_threshold]
        
    # Create clear visualization
    plt.figure(figsize=(10, 8))
    
    # Good layout
    pos = nx.spring_layout(G_sub, seed=42, k=2, iterations=50)
    
    # Prepare colors and sizes
    node_colors = []
    node_sizes = []
    
    for node in G_sub.nodes():
        degree = sub_degrees[node]
        if node in popular_pages:
            node_colors.append('red')
            node_sizes.append(100 + degree * 8)
        else:
            node_colors.append('lightblue')
            node_sizes.append(50 + degree * 5)
    
    # Draw network
    nx.draw_networkx_edges(G_sub, pos, 
                          edge_color='lightgray', 
                          width=0.8, 
                          alpha=0.6)
    
    nx.draw_networkx_nodes(G_sub, pos,
                          node_size=node_sizes,
                          node_color=node_colors,
                          alpha=0.8,
                          edgecolors='black',
                          linewidths=0.5)
    
    # Clear title
    plt.title("Facebook Page-Page Network (Sample)\n" +
             "Red = Popular pages (many connections), Blue = Regular pages (fewer connections)\n" +
             f"{G_sub.number_of_nodes()} pages, {G_sub.number_of_edges()} connections",
             fontsize=14, pad=20)
    
    plt.axis('off')
    
    # Simple legend
    red_dot = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                        markersize=12, label=f'Popular pages ({len(popular_pages)})')
    blue_dot = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', 
                         markersize=10, label=f'Regular pages ({len(regular_pages)})')
    plt.legend(handles=[red_dot, blue_dot], loc='upper right', fontsize=12)
    
    plt.tight_layout()
    plt.show()
    
    print("\n=== WHAT THIS SHOWS ===")
    print("✓ Facebook pages form a network - some are connected to others")
    print("✓ Popular pages (red) have many connections - they're 'hubs'")
    print("✓ Regular pages (blue) have fewer connections")
    
    popular_degrees = [sub_degrees[node] for node in popular_pages]
    regular_degrees = [sub_degrees[node] for node in regular_pages]
    
    print(f"\nNumbers:")
    print(f"• Popular pages average {np.mean(popular_degrees):.1f} connections each")
    print(f"• Regular pages average {np.mean(regular_degrees):.1f} connections each")
    print(f"• Most connected page has {max(sub_degrees.values())} connections")
    
    return G_sub