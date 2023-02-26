from decouple import config
import sqlalchemy as db

class SqlConnector:
    def __init__(self, db):
        self.db = db
        self.env = 'prod'
        self.driver = "mysql+pymysql"
        self.host = config("DB_HOST")
        self.password = config("DB_PASSWORD")
        self.username = config("DB_USERNAME")
        #self.port = os.getenv("DB_PORT")


    def get_engine(self):
        params = dict(
            drivername=self.driver,
            username=self.username,
            password=self.password,
            database=self.db,
            host=self.host,
            #port=self.port,
        )
        # if self.driver == "mysql+pymysql" :
        #     params["query"] = {"charset": "utf8mb4"}
        return db.create_engine(
            db.engine.url.URL.create(**params),
            pool_pre_ping=True,
            pool_size=10
        )

badminton_db = SqlConnector(db="badminton").get_engine()