from sqlalchemy import create_engine

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/example', echo=False) # echo=True
