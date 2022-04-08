# darbiadev-businesscentral
A wrapper for Business Central's API.

### Example usage
```python
from darbiadev_businesscentral import BusinessCentralServices

client = BusinessCentralServices(
    base_url="https://api.businesscentral.dynamics.com/v2.0/",
    tenant_id="00000000-0000-0000-0000-000000000000",
    environment="Production",
    company_name="My company",
    client_id="00000000-0000-0000-0000-000000000000",
    client_secret="secret",
)
print(client.make_request("get", "salesDocuments"))
```
