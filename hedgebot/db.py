import sqlite3
import os
import pandas as pd
from typing import Optional, Tuple, Any


class SQLiteManager:
    """A class for managing an SQLite database."""

    def __init__(self, db_name: str) -> None:
        """
        Initialize the SQLiteManager instance.

        Parameters:
            db_name (str): The name of the SQLite database file.
        """
        self.db_name: str = db_name
        self.connection: sqlite3.Connection
        self.cursor: sqlite3.Cursor
        self._create_database()

    def _create_database(self) -> None:
        """Create the SQLite database file if it doesn't exist."""
        if not os.path.exists(self.db_name):
            open(self.db_name, "a").close()

    def connect(self) -> None:
        """Connect to the SQLite database."""
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def disconnect(self) -> None:
        """Disconnect from the SQLite database."""
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """
        Execute an SQL query and return the result as a Pandas DataFrame if available.

        Parameters:
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame or None: A Pandas DataFrame containing the result of the query if available,
                                otherwise None.
        """
        try:
            self.connect()
            self.cursor.execute(query)
            self.connection.commit()
            result = self.cursor.fetchall()
            if result:
                df = pd.DataFrame(result, columns=[description[0] for description in self.cursor.description])
                return df
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            self.disconnect()

    def table(self, table_name: str, columns: dict[str, str]) -> None:
        """
        Create a table in the SQLite database.

        Parameters:
            table_name (str): The name of the table to create.
            columns (dict): A dictionary where keys are column names and values are column types.
        """
        columns_str = ", ".join([f"{name} {data_type}" for name, data_type in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (ID INTEGER PRIMARY KEY, {columns_str})"
        self.execute_query(query)

    def drop_table(self, table_name: str) -> None:
        """
        Drop a table from the SQLite database.

        Parameters:
            table_name (str): The name of the table to drop.
        """
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.execute_query(query)

    def delete_row(self, table_name: str, condition: str) -> None:
        """
        Delete rows from the specified table based on a condition.

        Parameters:
            table_name (str): The name of the table to delete from.
            condition (str): The condition to specify which rows to delete.
        """
        query = f"DELETE FROM {table_name} WHERE {condition}"
        try:
            self.connect()
            self.cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error deleting rows: {e}")
        finally:
            self.disconnect()
