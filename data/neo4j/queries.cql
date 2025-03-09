LOAD CSV WITH HEADERS FROM 'file:///funnel.csv' AS row
MERGE (s:Segment {name: row.`Segment Name`})
MERGE (v:Vertical {name: row.Vertical})
MERGE (p:Product {name: row.Product})
MERGE (s)-[:BELONGS_TO]->(v)
MERGE (s)-[:ASSOCIATED_WITH]->(p);