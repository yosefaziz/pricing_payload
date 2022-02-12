from sqlalchemy import create_engine
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PayloadToDB:
    def __init__(self):
        self.payload_file_path = "price_payload.json"
        self.disk_engine = create_engine("sqlite:///payload_database.db")

    def read_payload(self) -> pd.DataFrame:
        """Reads the .json-File into a pandas dataframe.

        Returns:
            payload_df: Pricing payload dataframe
        """
        schema = {"product": "int", "timestamp": "datetime64", "price": "numeric"}
        payload_df = pd.read_json(self.payload_file_path, dtype=schema)
        logging.info("JSON-file read as a pandas dataframe")
        return payload_df

    @staticmethod
    def drop_null_prices(payload_df: pd.DataFrame) -> pd.DataFrame:
        """In case there are null values in the prices column, this function drops these rows.

        Args:
            payload_df: Pricing payload dataframe
        Returns:
            payload_df: Pricing payload dataframe, excluding rows with null in the price column
        """
        payload_df["price"] = payload_df["price"].dropna()
        logging.info("Null-Prices dropped")
        return payload_df

    def payload_to_db(self, payload_df: pd.DataFrame) -> None:
        """Inserts the dataframe into the database.

        Args:
            payload_df: Pricing payload dataframe
        Returns:
            None
        """
        with self.disk_engine.connect() as conn:
            # the DROP TABLE logic is only for demo purposes
            conn.execute("DROP TABLE IF EXISTS pricing;")
            payload_df.to_sql(name="pricing", con=conn, if_exists="append", index=False)
        logging.info("JSON-file inserted in DB")

    def json_source_to_db(self) -> None:
        """Main function to orchestrate the pipeline from JSON to the Database.

        Returns:
            None
        """
        payload_df = self.read_payload()
        payload_df = self.drop_null_prices(payload_df)
        self.payload_to_db(payload_df)
