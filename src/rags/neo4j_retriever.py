from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore
from llama_index.core.retrievers import BaseRetriever
from neo4j import GraphDatabase
from collections import Counter
from typing import List

class Neo4jRetriever(BaseRetriever):
    """Neo4j retriever that performs search on a Neo4j database."""

    def __init__(
        self
    ) -> None:
        """Init params."""
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes given query."""
        # Split query into keywords, remove common words, and clean up
        keywords = [word.lower().strip() for word in query_bundle.query_str.split()
                   if len(word) > 2 and not word.lower() in ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']]
        
        nodes = self._fetch_nodes(keywords)
        return nodes

    def _fetch_nodes(self, keywords: List[str]) -> List[NodeWithScore]:
        """Fetch nodes from Neo4j."""

        # Connect to Neo4j
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

        # Build Cypher query to match nodes containing any of the keywords
        query = """
        MATCH (n:Segment)
        WHERE any(keyword IN $keywords WHERE toLower(n.content) CONTAINS toLower(keyword))
        RETURN n.content as text, n.someId as id
        """
        
        nodes = []

        # Execute query and get results
        with driver.session() as session:
            result = session.run(query, keywords=keywords)
            for record in result:
                # Create NodeWithScore for each matching segment
                node = NodeWithScore(
                    node=record["text"],
                    # Calculate BM25 score based on term frequency and document length
                    score=self._calculate_bm25_score(record["text"], keywords)
                )
                nodes.append(node)

        driver.close()
        return nodes
        

    def _calculate_bm25_score(self, text: str, keywords: List[str]) -> float:
        """Calculate BM25 score for a given text and keywords."""
        # Tokenize text and keywords
        tokens = text.split()
        keyword_counts = Counter(keywords)

        # Calculate BM25 score
        score = 0
        for token in tokens:
            if token in keyword_counts:
                score += keyword_counts[token]

        return score