from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

MEMGRAPH_URI = os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")
MEMGRAPH_USER = os.getenv("MEMGRAPH_USER", "")
MEMGRAPH_PASSWORD = os.getenv("MEMGRAPH_PASSWORD", "")

driver = GraphDatabase.driver(
    MEMGRAPH_URI,
    auth=(MEMGRAPH_USER, MEMGRAPH_PASSWORD)
)


def check_memgraph():
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        return result.single()["test"]