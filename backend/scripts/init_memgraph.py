from backend.app.services.memgraph_service import driver


def init_memgraph():
    with driver.session() as session:
        result = session.run("SHOW INDEX INFO;")

        existing_indexes = list(result)

        user_index_exists = any(
            record["label"] == "User"
            and "id" in record["property"]
            for record in existing_indexes
        )

        if not user_index_exists:
            session.run("CREATE INDEX ON :User(id);")
            print("Created User.id index.")
        else:
            print("User.id index already exists.")


if __name__ == "__main__":
    init_memgraph() 