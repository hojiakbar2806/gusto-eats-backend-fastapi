from sqlalchemy import create_engine

connection_string = "postgresql://hojiakbar:CVBMdsdpSYOav1uCjpRIcXlTdjhktvQn@dpg-cqho0d08fa8c73bvpsg0-a/gusto_eats"
engine = create_engine(connection_string)

try:
    with engine.connect() as connection:
        print("Connection to PostgreSQL DB successful")
except Exception as e:
    print(f"The error '{e}' occurred")
