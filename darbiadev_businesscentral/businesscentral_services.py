#!/usr/bin/env python

from datetime import datetime, timedelta

import requests


class BusinessCentralServices:
    """
    This class wraps Business Central's API, only ODataV4 is implemented.
    """

    def __init__(
        self, base_url: str, tenant_id: str, environment: str, company_name: str, client_id: str, client_secret: str
    ):
        self.base_url: str = base_url
        self.__tenant_id: str = tenant_id
        self.environment: str = environment
        self.company_name: str = company_name
        self.__client_id: str = client_id
        self.__client_secret: str = client_secret
        self.__oauth_token: str = ""
        self.__oauth_token_expires_at: datetime = datetime.now()

        self.token_url = f"https://login.microsoftonline.com/{self.__tenant_id}/oauth2/v2.0/token"
        self.odata_base_url: str = base_url + f"{self.__tenant_id}/{self.environment}/ODataV4/"
        self.odata_company: str = f"Company('{company_name}')/"
        self.odata_url: str = self.odata_base_url + self.odata_company

    def _update_token(self) -> None:
        if self.__oauth_token_expires_at < datetime.now():
            response = requests.post(
                url=self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "scope": "https://api.businesscentral.dynamics.com/.default",
                    "client_id": self.__client_id,
                    "client_secret": self.__client_secret,
                },
            ).json()
            self.__oauth_token = response["access_token"]
            self.__oauth_token_expires_at = datetime.now() + timedelta(hours=1)

    def _build_resource_url(
        self,
        resource: str,
        values: list[str] = None,
    ):
        if values is None:
            values = []
        resource_url = f"/{resource}"
        if len(values) == 0:
            pass
        elif len(values) == 1:
            resource_url += f"({values[0]})"
        elif len(values) > 1:
            resource_url += "("
            for value in values:
                if isinstance(value, int):
                    resource_url += str(value) + ","
                else:
                    resource_url += f"'{value}',"
            resource_url = resource_url[:-1] + ")"
        return self.odata_url + resource_url

    def _build_unbound_action_url(self, codeunit: str, procedure: str) -> str:
        return self.odata_base_url + f"{codeunit}_{procedure}/"

    def make_request(
        self,
        method: str,
        resource: str,
        resource_data: dict[str, str | int | bool] = None,
        values: list[str] = None,
        params: dict[str, str] = None,
        etag: str = None,
    ) -> dict:
        self._update_token()

        args = {
            "method": method,
            "url": self._build_resource_url(resource=resource, values=values),
            "headers": {"Content-Type": "application/json", "Authorization": f"Bearer {self.__oauth_token}"},
        }

        if resource_data is not None:
            args["json"] = resource_data

        if etag is not None:
            args["headers"]["If-Match"] = etag

        if params is not None:
            args["params"] = params

        response = requests.request(**args)
        return response.json()

    def make_unbound_request(self, codeunit: str, procedure: str, data: dict[str, str]) -> dict:
        self._update_token()

        args = {
            "method": "POST",
            "url": self._build_unbound_action_url(codeunit=codeunit, procedure=procedure),
            "headers": {"Content-Type": "application/json", "Authorization": f"Bearer {self.__oauth_token}"},
            "params": {"company": self.company_name},
            "json": data,
        }

        response = requests.request(**args)
        return response.json()
