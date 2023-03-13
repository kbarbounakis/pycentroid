import re

def trim_field_reference(name:str):
    return re.sub(r'\$(\w+)', r'\1', name)

def format_collection_reference(name:str):
    return re.sub(r'\$?(\w+)', r'$\1', name)

def format_field_reference(name:str):
    return re.sub(r'\$?(\w+)', r'$\1', name)

def format_any_field_reference(name:str):
    return re.sub(r'^\$?(\w+)', r'$\1', name)

def get_first_key(any: dict):
    """Returns the first key of a dictionany

    Args:
        any (dict): Any dictionary

    Returns:
        str
    """
    for key in any:
        return key
        

class QueryField(dict):
    def __init__(self, name: str):
        self.__setitem__(trim_field_reference(name), 1)

    def from_(self, collection: str):
        key :str= get_first_key(self)
        if key is None:
            raise 'Field name cannot be empty when defining collection'
        if key.startswith('$'):
            raise 'Unsupported field expression. Define collection before assigning an expression'
        value = self.__getitem__(key)
        self.__delitem__(key)
        key = trim_field_reference(collection) + '.' + key;
        self.__setitem__(key, 1)
        return self;
    
    def as_(self, alias: str):
        key :str= get_first_key(self)
        if key is None:
            raise 'Field name cannot be empty when defining an alias'
        value = self.__getitem__(key)
        self.__delitem__(key)
        self.__setitem__(alias, {
            key: value
        })
        return self

    def __use_datetime_function__(self, date_function, timezone = None):
        field :str= get_first_key(self)
        value = self.__getitem__(field)
        if type(value) is int:
            value = format_any_field_reference(field);
        self.__delitem__(field)
        self.__setitem__(date_function, {
                'date': value,
                'timezone': timezone
            })
        return self

    def __use_method_call__(self, method, *args):
        field :str= get_first_key(self)
        value = self.__getitem__(field)
        if type(value) is int and value == 1:
            value = format_any_field_reference(field)
        self.__delitem__(field)
        arguments = []
        arguments.append(value)
        for a in args:
            if (type(a) is QueryField):
                field :str= get_first_key(a)
                value = a.__getitem__(field)
                if type(value) is int and value == 1:
                    arguments.append(format_any_field_reference(field))
                else:
                    arguments.append(a)
            else:
                arguments.append(a)
        self.__setitem__(method, arguments)
        return self
    
    def get_year(self, timezone = None):
        return self.__use_datetime_function__('$year', timezone)
    
    def year(self, timezone = None):
        return self.get_year(timezone);

    def get_date(self, timezone = None):
        return self.__use_datetime_function__('$dayOfMonth', timezone)
    
    def day(self, timezone = None):
        return self.get_date(timezone);
    
    def get_month(self, timezone = None):
        return self.__use_datetime_function__('$month', timezone)
    
    def month(self, timezone = None):
        return self.get_month(timezone);

    def get_hours(self, timezone = None):
        return self.__use_datetime_function__('$hour', timezone)
    
    def hour(self, timezone = None):
        return self.get_hours(timezone);
    
    def get_minutes(self, timezone = None):
        return self.__use_datetime_function__('$minute', timezone)
    
    def minute(self, timezone = None):
        return self.get_minutes(timezone);

    def get_seconds(self, timezone = None):
        return self.__use_datetime_function__('$second', timezone)
    
    def second(self, timezone = None):
        return self.get_seconds(timezone);
    
    def length(self):
        return self.__use_method_call__('$size')
    
    def len(self):
        return self.length('$size')
    
    def trim(self):
        return self.__use_method_call__('$trim')
    
    def ceil(self):
        return self.__use_method_call__('$ceil')
    
    def floor(self):
        return self.__use_method_call__('$floor')
    
    def round(self, digits):
        return self.__use_method_call__('$round', digits)
    
    def add(self, value):
        return self.__use_method_call__('$add', value);
    
    def subtract(self, value):
        return self.__use_method_call__('$subtract', value);

    def multiply(self, value):
        return self.__use_method_call__('$multiply', value);
    
    def divide(self, value):
        return self.__use_method_call__('$divide', value);
    
    def modulo(self, value = 2):
        return self.__use_method_call__('$mod', value);
    
    def concat(self, *args):
        return self.__use_method_call__('$concat', *args);
    
    def substring(self, start, length):
        return self.__use_method_call__('$substr', start, length);

