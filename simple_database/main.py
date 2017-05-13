import os, json
from datetime import date

from simple_database.exceptions import ValidationError
from simple_database.config import BASE_DB_FILE_PATH


class Row(object):
    def __init__(self, row):
        for key, value in row.items():
            setattr(self, key, value)


class Table(object):

    def __init__(self, db, name, columns=None):
        self.db = db
        self.name = name

        self.table_filepath = os.path.join(BASE_DB_FILE_PATH, self.db.name,
                                           '{}.json'.format(self.name))

        # In case the table JSON file doesn't exist already, you must
        # initialize it as an empty table, with this JSON structure:
        # {'columns': columns, 'rows': []}
        if not os.path.isfile(self.table_filepath):
            with open(self.table_filepath, 'w+') as f:
                json.dump({'columns': columns, 'rows': []}, f)
                
                
        self.columns = columns or self._read_columns()

    def _read_columns(self):
        # Read the columns configuration from the table's JSON file
        # and return it.
        with open(self.table_filepath, 'r') as file:
            data = json.load(file)
            return data['column']

    def insert(self, *args):
        # Validate that the provided row data is correct according to the
        # columns configuration.
        # If there's any error, raise ValidationError exception.
        # Otherwise, serialize the row as a string, and write to to the
        # table's JSON file.
        # Check length, if != raise Validation
        if len(args) != len(self.columns):
            raise ValidationError('Invalid amount of fields.')
            
        rows_to_add = []
        for arg, col in zip(args, self.columns):
            if type(arg).__name__ == col['type']:
                if isinstance(arg, date):
                    arg = str(arg)
                serialized = {}
                serialized[col['name']] = "{}".format(arg)
                rows_to_add.append(serialized) 
            else:
                raise ValidationError('Invalid type of field "{}": Given "{}", expected "{}"'.format(arg, col['type'],
                                                                                                     type(arg).__name__))
        # Port args over to .json file
        with open(self.table_filepath, 'r+') as f:
            
            json_file = json.load(f)
            if len(rows_to_add) == 0:
                pass
            
            for row in rows_to_add:
                json_file['rows'] +=  row
                
            f.seek(0)
            f.write(json.dumps(json_file))
        """
        {
            'cols': [lsist of dicts],
            'rows':[
            {'firstname': }
            
            ]
        }
        """
        
    def query(self, **kwargs):
        # Read from the table's JSON file all athe rows in the current table
        # and return only the ones that match with provided arguments.
        # We would recomment to  use the `yield` statement, so the resulting
        # iterable object is a generator.

        # IMPORTANT: Each of the rows returned in each loop of the generator
        # must be an instance of the `Row` class, which contains all columns
        # as attributes of the object.
        pass

    def all(self):
        # Similar to the `query` method, but simply returning all rows in
        # the table.
        # Again, each element must be an instance of the `Row` class, with
        # the proper dynamic attributes.
        pass

    def count(self):
        # Read the JSON file and return the counter of rows in the table
        pass

    def describe(self):
        # Read the columns configuration from the JSON file, and return it.
        pass


class DataBase(object):
    def __init__(self, name):
        self.name = name
        self.db_filepath = os.path.join(BASE_DB_FILE_PATH, self.name)
        self.tables = self._read_tables()

    @classmethod
    def create(cls, name):
        filepath = os.path.join(BASE_DB_FILE_PATH, name)
        # if the db directory already exists, raise ValidationError
        # otherwise, create the proper db directory
        if os.path.exists(filepath):
            raise ValidationError
        else:
            os.makedirs(filepath)

    def _read_tables(self):
        # Gather the list of tables in the db directory looking for all files
        # with .json extension.
        # For each of them, instatiate an object of the class `Table` and
        # dynamically assign it to the current `DataBase` object.
        # Finally return the list of table names.
        # Hint: You can use `os.listdir(self.db_filepath)` to loop through
        #       all files in the db directory
        tables = [Table(self.db_filepath, table.strip('.json')) for table in os.listdir(self.db_filepath)]
        for table in tables:
            setattr(self, table.name, table) # sets db.table_name = table
        return tables
        """
        
        my_obj = object()
        setattr(my_obj, 'the_list', [1,2,3])
        my_obj.the_list[0] == 1
            
        """

    def create_table(self, table_name, columns):
        # Check if a table already exists with given name. If so, raise
        # ValidationError exception.
        # Otherwise, create an instance of the `Table` class and assign
        # it to the current db object.
        # Make sure to also append it to `self.tables`
        if table_name in self.tables:
            raise ValidationError('Database with name "{}" already exists.'.format(table_name))
        else:
            new_table = Table(self, table_name, columns)
            self.tables.append(new_table)
            setattr(self, new_table.name, new_table)

    def show_tables(self):
        # Return the current list of tables.
        return [table.name for table in self.tables]


def create_database(db_name):
    """
    Creates a new DataBase object and returns the connection object
    to the brand new database.
    """
    DataBase.create(db_name)
    return connect_database(db_name)


def connect_database(db_name):
    """
    Connects to an existing database, and returns the connection object.
    """
    return DataBase(name=db_name)
