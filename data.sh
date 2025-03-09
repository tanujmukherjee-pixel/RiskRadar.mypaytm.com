#!/bin/bash

# Define Neo4j credentials
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="password"
NEO4J_URI="bolt://localhost:7687"

# Execute the Cypher queries using cypher-shell
cypher-shell -u $NEO4J_USERNAME -p $NEO4J_PASSWORD -a $NEO4J_URI < queries.cql

echo "Ontology graph for funnel hub definition populated in Neo4j."
