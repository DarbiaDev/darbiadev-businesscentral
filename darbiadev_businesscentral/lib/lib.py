#!/usr/bin/env python

import json
from typing import Union
from urllib.parse import quote

import requests


class BusinessCentralServices:
    """A class wrapping Business Central's API.

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
        self.tenant_id: str = tenant_id
        self.environment: str = environment
        self.company_name: str = company_name
        self.username: str = username
        self.web_service_access_key: str = web_service_access_key

        self.odata_base_url: str = base_url + f'{self.tenant_id}/{self.environment}/ODataV4/'
        self.odata_company: str = f"Company('{quote(company_name)}')/"
        self.odata_url: str = self.odata_base_url + self.odata_company

    def _build_resource_url(
            self,
            resource: str,
            values: list[str] = None,
            query: str = None
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
        if query:
            resource_url += query
        return self.odata_url + resource_url

    def _make_request(
            self,
            method: str,
            resource: str = None,
            resource_data: dict[str, Union[str, int, bool]] = None,
            values: list[str] = None,
            query: str = None,
            etag: str = None,
    ) -> dict:
        args = {
            'method': method,
            'url': self._build_resource_url(resource=resource, values=values, query=query),
            'auth': (self.username, self.web_service_access_key),
            'headers': {'Content-Type': 'application/json'}
        }

        if resource_data is not None:
            args['data'] = json.dumps(resource_data)

        if etag is not None:
            args['headers']['If-Match'] = etag

        response = requests.request(**args)
        return response.json()
