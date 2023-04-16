from sqlalchemy import create_engine, text


def get_db_engine(db_uri):
    db_engine = create_engine(
        db_uri,
        connect_args={"connect_timeout": 900, "options": "-csearch_path=real_db"},
    )
    return db_engine


def query_db(query, db_uri):
    sql = text(query)
    engine = create_engine(db_uri)
    with engine.begin() as con:
        results = con.execute(sql)
    return results


def insert_query_db(query, db_uri):
    sql = text(query)
    engine = create_engine(db_uri)
    with engine.begin() as con:
        con.execute(sql)
