from themost_framework.common.objects import object
from themost_framework.query import OpenDataQueryExpression, OpenDataFormatter, QueryEntity
from themost_framework.common import expect, AnyObject
import requests
from requests.structures import CaseInsensitiveDict
from urllib.parse import urljoin
import json
import re
import xml.etree.ElementTree as ElementTree
from .metadata import EdmSchema

NSMAP = {
    'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
    'edm': 'http://docs.oasis-open.org/odata/ns/edm'
}

class ClientContextOptions():
    remote=None
    def __init__(self, remote):
        self.remote = remote


class ClientDataService():
    def __init__(self, options):
        self.options = options
        self.headers = CaseInsensitiveDict()
    
    def set(self, key: str, value):
        """Sets an HTTP header that is going to be included in remote requests

        Args:
            key (str): The name of the HTTP header
            value (*): The value of the HTTP header
        """
        self.headers.update([
            [
                key,
                value
            ]
        ])

    def pop(self, key):
        """Removes an HTTP header

        Args:
            key (str): The name of the HTTP header
        """
        self.headers.pop(key)
    
    def resolve(self, url: str) -> str:
        """Resolves an absolute url 

        Args:
            url (str): A string which represents a relative url

        Returns:
            str: The absolute url which has been resolved
        """
        expect(re.search(r'^((https?):\/\/)', url)).to_be_falsy(Exception('Expected relative url'))
        return urljoin(self.options.remote, url)
        

class ClientDataModel():
    service = None
    def __init__(self, name):
        self.name = name
    
    def as_queryable(self):
        """Gets an instance of client queryable which is going to be used to get items

        Returns:
            ClientDataQueryable: An instance of client queryable
        """
        return ClientDataQueryable(self)

    @property
    def url(self):
        return urljoin(self.service.options.remote, self.name)

    def execute(self, data:dict):
        # get url e.g. /Orders
        url = self.url
        # get headers
        headers = self.model.service.headers.copy()
        # make request and send data
        response = requests.post(url, json=data, headers=headers)
        # get response
        return response.json()
    
    def save(self, data:dict):
        return self.execute(data)

    def remove(self, item:dict):
        # get url e.g. /Orders/1234000
        url = urljoin(self.url, item)
        # get service headers
        headers = self.model.service.headers.copy()
        # make request
        response = requests.delete(url, headers=headers)
        # get response, if any
        return response.json()


class ClientDataQueryable(OpenDataQueryExpression):

    model = None
    def __init__(self, model: ClientDataModel):
        super().__init__(QueryEntity(model.name))
        self.__model__ = model

    @property
    def params(self):
        return OpenDataFormatter().format(self)

    @property
    def url(self) -> str:
        """Gets the current absolute url

        Returns:
            str: A string which represents the absolute url of a service
        """
        return urljoin(self.__model__.service.options.remote, self.__model__.name)

    def get_items(self):
        """Returns a collection of items based on the given query

        Returns:
            list(*): A collection of items 
        """
        # get url
        url = self.url
        # get headers
        headers = self.__model__.service.headers.copy()
        # get query params
        params = self.params
        # add accept header
        if not 'Accept' in headers:
            headers.update([
                [
                    'Accept',
                    'application/json'
                ]
            ])
        # make request
        response = requests.get(url, params, headers = headers)
        result = response.json()
        if 'value' in result and type(result['value']) is list:
            return result['value']
        return result

    def get_item(self):
        """Returns an item based on the given query

        Returns:
            *: The item which meets the filter provided
        """
        url = self.url
        headers = self.__model__.service.headers.copy()
        params = self.params
        params.update([
            [
                '$top', 1
            ],
            [
                '$skip', 0
            ],
            [
                '$count', 'false'
            ]
        ])
        if not 'Accept' in headers:
            headers.update([
                [
                    'Accept',
                    'application/json'
                ]
            ])
        response = requests.get(url, params, headers = headers)
        result = response.json()
        key = 'value'
        if key in result and type(result[key]) is list:
            if len(result[key]) > 0:
                return result[key][0]
            else:
                return None
        return result


class ClientDataContext():

    __metadata__ = None

    def __init__(self, options):
        self.service = ClientDataService(options)
    
    def model(self, name):
        """Returns an instance of a client data model for further processing

        Args:
            name (_type_): The name of the remote data model

        Returns:
            ClientDataModel: The instance of data model
        """
        model = ClientDataModel(name)
        model.service = self.service
        return model
    
    def get_metadata(self):
        if self.__metadata__ is not None:
            return self.__metadata__
        url = self.service.resolve('$metadata')
        headers = self.service.headers.copy()
        response = requests.get(url, headers=headers)
        text = response.text
        doc = ElementTree.fromstring(text)
        element = doc.find('edmx:DataServices/edm:Schema', {
            'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
            'edm': 'http://docs.oasis-open.org/odata/ns/edm'
        })
        self.__metadata__ = EdmSchema().__readxml__(element)
        return self.__metadata__


