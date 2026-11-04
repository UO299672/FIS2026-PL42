from util.database import Database

class lista_esperaModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = Database(db_name)
