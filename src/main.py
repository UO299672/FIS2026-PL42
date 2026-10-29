from util.database import DataBase

def initialize_database(db_name="CompanyDB.db", schema_path="resources/schema.sql", data_path="resources/data.sql"):
    db = DataBase(db_name)
    db.executeScript(schema_path)  # Load schema
    db.executeScript(data_path)    # Load initial data

def main():
    initialize_database()  # Initialize DB with schema and data on each run
        
    while True:    
        print("Panel de funcionalidades:")
        
        choice = input("Seleccione una opción: ").strip()
        


if __name__ == "__main__":
    main()