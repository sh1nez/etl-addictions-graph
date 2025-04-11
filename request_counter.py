import matplotlib.pyplot as plt
from collections import Counter
import re
#reading a sql-file
def read_sql_queries(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        queries = file.readlines()

    sql_command_pattern = re.compile(r'^\s*(SELECT|INSERT|UPDATE|DELETE)', re.IGNORECASE)

    filtered_queries = [
        query.strip() for query in queries
        if sql_command_pattern.match(query)
    ]

    return filtered_queries
#counter and line 
def plot_query_frequencies(queries):
    query_counts = Counter(queries)
    labels, values = zip(*query_counts.items())
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for i, (label, value) in enumerate(query_counts.items()):
        ax.plot([0, value], [i, i], linewidth=max(2, value * 0.8), label=f"{label} ({value} times)", color='skyblue')

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_xlabel('Frequency')
    ax.set_title('Frequency of SQL Queries')
    ax.set_xlim(0, max(values) + 1)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)


    plt.tight_layout()
    plt.subplots_adjust(left=0.2, bottom=0.2)  

  
    plt.show()


queries = read_sql_queries('001.sql')
plot_query_frequencies(queries)
