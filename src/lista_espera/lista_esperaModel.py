from util.database import DataBase

class lista_esperaModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = DataBase(db_name)
