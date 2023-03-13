from .query_field import QueryField, get_first_key, format_any_field_reference

class UnknownPropertyException(Exception):
    """Query property not set"""
    pass


class QueryExpression:
    def __init__(self):
        self.__query = None
        self.__left = None
        self.__last_logical = None
        return

    def where(self, name: str):
        self.__query = None
        # todo: validate object name
        self.__left = QueryField(name)
        return self

    def equal(self, value):
        left = self.__left;
        if left is None:
            raise UnknownPropertyException
        self.__append({
            '$eq': [
                self.left,
                value
            ]
        })
        return self

    def equals(self, value):
        return self.equal(value)

    def not_equal(self, value):
        if self.__left is None:
            raise UnknownPropertyException
        self.__append({
            '$ne': [
                self.__left,
                value
            ]
        })
        return self

    def not_equals(self, value):
        return self.not_equal(value)

    def greater_than(self, value):
        if self.__left is None:
            raise UnknownPropertyException
        self.__append({
            '$gt': [
                self.__left,
                value
            ]
        })
        return self

    def greater_or_equal(self, value):
        if self.__left is None:
            raise UnknownPropertyException
        self.__append({
            '$gte': [
                self.__left,
                value
            ]
        })
        return self

    def lower_than(self, value):
        if self.__left is None:
            raise UnknownPropertyException
        self.__append({
            '$lt': [
                self.__left,
                value
            ]
        })
        return self

    def lower_or_equal(self, value):
        if self.__left is None:
            raise UnknownPropertyException
        self.__append({
            '$lte': [
                self.__left,
                value
            ]
        })
        return self

    def and_(self, name: str):
        self.__left = QueryField(name)
        self.__last_logical = '$and'
        return self

    def or_(self, name: str):
        self.__left = QueryField(name)
        self.__last_logical = '$or'
        return self
    
    def get_year(self, timezone = None):
        self.__left:QueryField.get_year(timezone)
        return self

    def get_date(self, timezone = None):
        self.__left:QueryField.get_date(timezone)
        return self
    
    def get_month(self, timezone = None):
        self.__left:QueryField.get_month(timezone)
        return self

    def get_hours(self, timezone = None):
        self.__left:QueryField.get_hours(timezone)
        return self
    
    def hour(self, timezone = None):
        self.__left:QueryField.get_hours(timezone)
        return self
    
    def get_minutes(self, timezone = None):
        self.__left:QueryField.get_year(timezone)
        return self
    
    def minute(self, timezone = None):
        self.__left:QueryField.get_minutes(timezone)
        return self

    def get_seconds(self, timezone = None):
        self.__left:QueryField.get_seconds(timezone)
        return self
    
    def second(self, timezone = None):
        self.__left:QueryField.get_seconds(timezone)
        return self
    
    def index_of(self, value: str):
        self.__left = {
            '$indexOfBytes': [
                self.__left,
                value
            ]
        }
        return self

    def index(self, value: str):
        return self.index_of(value);
    
    def length(self):
        self.__left = {
            '$length': [
                self.__left
            ]
        }
        return self

    def to_lower(self):
        self.__left = {
            '$toLower': [
                self.__left
            ]
        }
        return self
    
    def to_upper(self):
        self.__left = {
            '$toUpper': [
                self.__left
            ]
        }
        return self

    def __append(self, expr):
        if self.__query is None:
            self.__query = expr
        else:
            # get first property of current query
            property = list(self.__query.keys())[0];
            # get logical operator
            logical_operator = self.__last_logical
            # if last logical operator is equal with this property
            if (property == logical_operator):
                # append query expression
                expr[property].append(expr)
            else:
                self.__query = {
                    logical_operator: [
                        self.__query.copy(),
                        expr
                    ]
                }

