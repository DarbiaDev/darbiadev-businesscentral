#!/usr/bin/env python

from typing import Union

import requests


class BusinessCentralServices:
    """
    This class wraps Business Central's API, only ODataV4 is implemented.
    """

    def __init__(
            self,
            base_url: str,
            tenant_id: str,
            environment: str,
            company_name: str,
            username: str,
            web_service_access_key: str
    ):
        self.base_url: str = base_url
        self.__tenant_id: str = tenant_id
        self.environment: str = environment
        self.company_name: str = company_name
        self.__username: str = username
        self.__web_service_access_key: str = web_service_access_key

        self.odata_base_url: str = base_url + f'{self.__tenant_id}/{self.environment}/ODataV4/'
        self.odata_company: str = f"Company('{company_name}')/"
        self.odata_url: str = self.odata_base_url + self.odata_company

    def _build_resource_url(
            self,
            resource: str,
            values: list[str] = None,
    ):
        if values is None:
            values = []
        resource_url = f'/{resource}'
        if len(values) == 0:
            pass
        elif len(values) == 1:
            resource_url += f'({values[0]})'
        elif len(values) > 1:
            resource_url += '('
            for value in values:
                if isinstance(value, int):
                    resource_url += str(value) + ','
                else:
                    resource_url += f"'{value}',"
            resource_url = resource_url[:-1] + ')'
        return self.odata_url + resource_url

    def _build_unbound_action_url(
            self,
            codeunit: str,
            procedure: str
    ):
        return self.odata_base_url + f'{codeunit}_{procedure}/'

    def _make_request(
            self,
            method: str,
            resource: str,
            resource_data: dict[str, Union[str, int, bool]] = None,
            values: list[str] = None,
            params: dict[str, str] = None,
            etag: str = None,
    ) -> dict:
        args = {
            'method': method,
            'url': self._build_resource_url(resource=resource, values=values),
            'auth': (self.__username, self.__web_service_access_key),
            'headers': {'Content-Type': 'application/json'}
        }

        if resource_data is not None:
            args['json'] = resource_data

        if etag is not None:
            args['headers']['If-Match'] = etag

        if params is not None:
            args['params'] = params

        response = requests.request(**args)
        response.raise_for_status()
        return response.json()

    def _make_unbound_request(
            self,
            codeunit: str,
            procedure: str,
            data: dict[str, str]
    ) -> dict:
        args = {
            'method': 'POST',
            'url': self._build_unbound_action_url(codeunit=codeunit, procedure=procedure),
            'auth': (self.__username, self.__web_service_access_key),
            'headers': {'Content-Type': 'application/json'},
            'params': {'company': self.company_name},
            'json': data
        }

        response = requests.request(**args)
        response.raise_for_status()
        return response.json()
