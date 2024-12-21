import datetime

#1
class Field:
    def __init__(self, field_type, max_length=None, null=False, default=None):
        self.field_type = field_type
        self.max_length = max_length
        self.null = null
        self.default = default

    def to_sql(self):
        type_mapping = {
            str: 'VARCHAR',
            int: 'INTEGER',
            datetime.date: 'DATE'
        }
        sql_type = type_mapping.get(self.field_type, 'TEXT')

        constraints = []
        if self.max_length:
            constraints.append(f'({self.max_length})')
        if not self.null:
            constraints.append('NOT NULL')
        if self.default is not None:
            constraints.append(f"DEFAULT '{self.default}'")

        return f"{sql_type} {' '.join(constraints)}"


#2
class CharField(Field):
    def __init__(self, max_length=255, null=False, default=''):
        super().__init__(str, max_length, null, default)

class IntegerField(Field):
    def __init__(self, null=False, default=0):
        super().__init__(int, null=null, default=default)

class DateField(Field):
    def __init__(self, null=False, default=datetime.date.today()):
        super().__init__(datetime.date, null=null, default=default)


#3
class ModelBase(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                fields[key] = value
                del attrs[key]
        new_class = super().__new__(cls, name, bases, attrs)
        new_class._fields = fields
        return new_class
    
    def _create_table(cls, table_name):
        columns = ', '.join(f"{name} {field.to_sql()}" for name, field in cls._fields.items())
        sql_command = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
        print(sql_command)


#4
class Model(metaclass=ModelBase):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        values = ', '.join(f"'{getattr(self, name)}'" for name in self._fields.keys())
        columns = ', '.join(self._fields.keys())
        sql_command = f"INSERT INTO {self.__class__.__name__.lower()} ({columns}) VALUES ({values});"
        print(sql_command)

    @classmethod
    def create_table(cls, table_name):
        cls._create_table(table_name)

#5
class Book(Model):
    title = CharField(max_length=255)
    author = CharField(max_length=100)
    published_date = DateField()
    year = IntegerField()


Book.create_table('books')


book = Book(
    title='Python Cookbook',
    author='David Beazley',
    published_date=datetime.date(2013, 5, 10),
    year=2012,
)
book.save()
