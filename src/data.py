from os.path import exists, join
from re import findall

import pandas as pd

from psycopg2 import connect

from src.config import load_config


def load_dataset(query: str):
    """Load dataset from cache or database"""

    path = join("data", "cache", f"{query}.csv")

    if not exists(path):
        df = fetch_dataset(query)
        df.to_csv(path, sep="\t", index=False)

    return pd.read_csv(path, sep="\t")


def fetch_dataset(query: str):
    """Fetch dataset from database using query in associated SQL file"""

    credentials = _parse_credentials(query)
    prepared_query = _prepare_query(query)

    connection = connect(**credentials)
    df = pd.io.sql.read_sql_query(prepared_query, connection)
    connection.close()

    return df


# ---------------------------- Private functions ------------------------------
# Build credentials dictionary based on key in header line in query SQL file
def _parse_credentials(query):
    # Query files should specify associated credentials on first line
    with open(_get_query_path(query)) as f:
        header = f.readline().strip()

    config = load_config("credentials")
    keys = {k for k, v in config.items() if type(v) is dict}

    prefix = "-- Credentials: "
    if not header.startswith(prefix):
        msg = f'Query "{query}" missing header "{prefix}[{", ".join(keys)}]"'
        raise QueryError(msg)

    key = header[len(prefix) :]

    if key not in keys:
        raise CredentialsError(f'Credentials "{key}" not found')

    credentials = {k: v for k, v in config.items() if type(v) is not dict}
    credentials = {**credentials, **config[key]}

    if not credentials["user"]:
        raise CredentialsError(f'Username for "{key}" not found')

    if not credentials["password"]:
        raise CredentialsError(f'Password for "{key}" not found')

    return credentials


# Build SQL query, replacing parameters with values read from config file
def _prepare_query(query):
    with open(_get_query_path(query)) as f:
        _ = f.readline()  # Skip credentials header line
        query_sql = f.read()

    # Extract query parameters from raw SQL
    params = [p[1:-1] for p in findall(r"{[a-zA-Z_][a-zA-Z_\d]*}", query_sql)]

    if not params:
        return query_sql

    args = load_config("queries")[query]

    missing = list(set(params).difference(args.keys()))
    if missing:
        raise QueryError(f'Query "{query}" missing argument(s): {missing}')

    unused = list(set(args.keys()).difference(params))
    if unused:
        raise QueryError(f'Unused argument(s) for query "{query}": {unused}')

    return query_sql.format(**args)


_get_query_path = lambda query: join("data", "queries", f"{query}.sql")


class CredentialsError(Exception):
    pass


class QueryError(Exception):
    pass
