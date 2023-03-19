
import re
from .query_expression import QueryExpression
from .query_field import get_first_key
from ..common import NotImplementError, expect
from .utils import SqlUtils
from .object_name_validator import ObjectNameValidator

class SqlDialectOptions:
    def __init__(self, name_format = r'\1', force_alias = True):
        self.name_format = name_format
        self.force_alias = force_alias

class SqlDialect:

    Space = ' '
    From = 'FROM'
    Where = 'WHERE'
    Select = 'SELECT'
    As = 'AS'

    def __init__(self, options = SqlDialectOptions()):
        self.options = options

    def escape(self, value, unquoted = True):
        if type(value) is dict:
            key = get_first_key(value)
            if (key.startswith('$')):
                func = getattr(self, '__' + key[1:] + '__')
                if not func is None:
                    params = value[key]
                    if type(params) is list:
                        return func(*params)
                    else:
                        return func(self, params)
            elif value[key] == 1:
                    # return object name
                    return self.escape_name(key)
        if type(value) is str and value.startswith('$'):
            return self.escape_name(value)
        return SqlUtils.escape(value)
    
    def escape_constant(self, value):
        return SqlUtils.escape(value)
    
    def escape_name(self, value):
        name = value if value.startswith('$') == False else value[1:]
        return  ObjectNameValidator().escape(name, self.options.name_format)

    def __eq__(self, left, right):
        final_right = self.escape(right)
        if final_right == 'NULL':
            return f'{self.escape(left)} IS NULL'
        return f'{self.escape(left)}={final_right}'
    
    def __ne__(self, left, right):
        final_right = self.escape(right)
        if final_right == 'NULL':
            return f'NOT {self.escape(left)} IS NULL'
        return f'{self.escape(left)}<>{final_right}'
    
    def __gt__(self, left, right):
        return f'{self.escape(left)}>{self.escape(right)}'

    def __gte__(self, left, right):
        return f'{self.escape(left)}>={self.escape(right)}'
    
    def __lt__(self, left, right):
        return f'{self.escape(left)}<{self.escape(right)}'
    
    def __lte__(self, left, right):
        return f'{self.escape(left)}<={self.escape(right)}'

    def __floor__(self, expr):
        return f'FLOOR({self.escape(expr)})'

    def __ceil__(self, expr):
        return f'CEILING({self.escape(expr)})'
    
    def __round__(self, expr, digits = 0):
        return f'ROUND({self.escape(expr)},{self.escape(digits)})'
    
    def __and__(self, *args):
        exprs = []
        for arg in args:
            exprs.append(self.escape(arg))
        result = '('
        result += ' AND '.join(exprs)
        result += ')'
        return result

    def __or__(self, *args):
        exprs = []
        for arg in args:
            exprs.append(self.escape(arg))
        result = '('
        result += ' OR '.join(exprs)
        result += ')'
        return result

    def __length__(self, expr):
        return f'LENGTH({self.escape(expr)})'

    def __trim__(self, expr):
        return f'TRIM({self.escape(expr)})'
    
    def __concat__(self, *args):
        exprs = []
        for arg in args:
            exprs.append(self.escape(arg))
        params_str = ','.join(exprs) 
        return f'CONCAT({params_str})'
    
    def __indexOfBytes__(self, expr, search):
        return f'(LOCATE({self.escape(search)},{self.escape(expr)}) - 1)'
    
    def __substr__(self, expr, pos, length = None):
        if length is None:
            return f'(SUBSTRING({self.escape(expr)},{self.escape(pos)} + 1))'
        return f'(SUBSTRING({self.escape(expr)},{self.escape(pos)} + 1, {self.escape(length)}))'
    
    def __toLower__(self, expr):
        return f'(LOWER({self.escape(expr)})'

    def __year__(self, expr):
        return f'(YEAR({self.escape(expr)})'
    
    def __month__(self, expr):
        return f'(MONTH({self.escape(expr)})'
    
    def __dayOfMonth__(self, expr):
        return f'(DAY({self.escape(expr)})'
    
    def __hour__(self, expr):
        return f'(HOUR({self.escape(expr)})'
    
    def __minute__(self, expr):
        return f'(MINUTE({self.escape(expr)})'
    
    def __second__(self, expr):
        return f'(SECOND({self.escape(expr)})'
    
    def __add__(self, **args):
        exprs = []
        for arg in args:
            exprs.append(self.escape(arg))
        result = '('
        result += '+'.join(exprs)
        result += ')'
        return result
    
    def __subtract__(self, **args):
        exprs = []
        for arg in args:
            exprs.append(self.escape(arg))
        result = '('
        result += '-'.join(exprs)
        result += ')'
        return result
    
    def __multiply__(self, *args):
        exprs = []
        for arg in args:
            exprs.append(self.escape(arg))
        result = '('
        result += '*'.join(exprs)
        result = ')'
        return result
    
    def __divide__(self, *args):
        exprs = []
        for arg in args:
            exprs.append(self.escape(arg))
        result = '('
        result += '/'.join(exprs)
        result += ')'
        return result
    
    def __modulo__(self, *args):
        exprs = []
        for arg in args:
            exprs.append(self.escape(arg))
        result = '('
        result += '%%'.join(exprs)
        result += ')'
        return result
    


class SqlFormatter:
    def __init__(self, dialect = None):
        self.__dialect__ = SqlDialect() if dialect is None else dialect
    
    def format_select(self, query:QueryExpression):
        expect(query.__collection__).to_be_truthy(Exception('Expected query collection'))
        sql = SqlDialect.Select
        if query.__select__ is None:
            sql +=' * ' # wildcard select
        else:
            fields = []
            for key in query.__select__:
                if query.__select__[key] == 1:
                    fields.append(self.__dialect__.escape_name(key))
                else:
                    fields.append(self.__dialect__.escape(query.__select__[key]) +
                    SqlDialect.Space +
                    SqlDialect.As +
                    SqlDialect.Space +
                    self.__dialect__.escape_name(key))
            sql += SqlDialect.Space
            sql += ','.join(fields)
            sql += SqlDialect.Space
        sql += SqlDialect.From
        sql += SqlDialect.Space
        
        sql += self.__dialect__.escape_name(query.__collection__.get_collection())
        if not query.__where__ is None:
            sql += SqlDialect.Space
            sql += SqlDialect.Where
            sql += sSqlDialect.Space
            sql += self.format_where(query.__where__)
        return sql

    def format_update(self, query:QueryExpression):
        raise NotImplementedError()
    
    def format_delete(self, query:QueryExpression):
        raise NotImplementedError()
    
    def format_insert(self, query:QueryExpression):
        raise NotImplementedError()
    
    def format_where(self, where):
        return self.__dialect__.escape(where)