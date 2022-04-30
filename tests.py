import logging
import sys

from neo4j import GraphDatabase, Transaction, Result


# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# logging.getLogger("neo4j").addHandler(handler)
# logging.getLogger("neo4j").setLevel(logging.DEBUG)


uri = "neo4j://94.250.248.156:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "qNBWTvaLPgaC2ARCzYMu2T8xnKMspZTwSEbE9panbXyKfRZGvUh45T4mV78chCfb"))


def create_persons(tx: Transaction):
    result: Result = tx.run("MERGE (alice:Person {name: 'Alice'}) RETURN alice")

    # raise RuntimeException("Do some with result which raises an exception")
    result: Result = tx.run("MERGE (bob:Person {name: 'Bob'}) RETURN bob")

    # no Alice and no Bob must be created


with driver.session() as session:
    session.write_transaction(create_persons)


def create_friend_of(tx: Transaction, name: str, friend: str):
    tx.run("MATCH (a:Person) WHERE a.name = $name "
           "CREATE (a)-[:KNOWS]->(:Person {name: $friend})",
           name=name, friend=friend)


with driver.session() as session:
    session.run("MATCH (a) DETACH DELETE a")
    session.write_transaction(create_persons)
    session.write_transaction(create_friend_of, "Alice", "Bob")
    session.write_transaction(create_friend_of, "Alice", "Carl")

    result: Result = session.run("MATCH (a) RETURN a")

driver.close()