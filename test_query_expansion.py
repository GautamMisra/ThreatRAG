
from pprint import pprint
from generation.query_expansion import expand_query

component = "Auth Service"
technology = "JWT"

print("=" * 60)
print("QUERY EXPANSION DIAGNOSTIC")
print("=" * 60)
print("Component:", component)
print("Technology:", technology)

expanded_queries = expand_query(component, technology)

print("\nGenerated queries:")
pprint(expanded_queries, sort_dicts=False)

print("\nQuery counts:")
for hop, queries in expanded_queries.items():
    print(f"{hop}: {len(queries)} queries")
