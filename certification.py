from sqlalchemy import create_engine
DATABASE_TYPE = 'postgresql'
DBAPI = 'psycopg2'
ENDPOINT = 'kashin.db.elephantsql.com' # Change it for your AWS endpoint
USER = 'ndpjaeig'
PASSWORD = '6CC7jnIs9o--70M_dy3Bf1GPF8ko1MWi'
PORT = 5432
DATABASE = 'ndpjaeig'
engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")