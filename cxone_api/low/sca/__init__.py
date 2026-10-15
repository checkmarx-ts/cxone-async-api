import requests, deprecation
from cxone_api import CxOneClient
from cxone_api.util import join_query_dict
from requests.compat import urljoin

@deprecation.deprecated(details="cxone_api.low.sca.export_service.create_a_report")
async def request_scan_report(client: CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring| Verb: POST Endpoint: /api/sca/export/requests

    .. deprecated:: 1.1.9
    Use: :func:`cxone_api.low.sca.export_service.create_a_report`
    
    """
    url = urljoin(client.api_endpoint, "sca/export/requests")
    return await client.exec_request(requests.post, url, json=kwargs)

@deprecation.deprecated(details="cxone_api.low.sca.export_service.retrieve_report_status")
async def get_scan_report_status(
    client: CxOneClient, exportId: str
) -> requests.Response:
    """|LowLevelApiDocstring| Verb: GET Endpoint: /api/sca/export/requests

    .. deprecated:: 1.1.9
    Use: :func:`cxone_api.low.sca.export_service.retrieve_report_status`
    """
    url = urljoin(client.api_endpoint, "sca/export/requests")
    url = join_query_dict(url, {"exportId": exportId})
    return await client.exec_request(requests.get, url)

@deprecation.deprecated(details="cxone_api.low.sca.export_service.download_a_report")
async def retrieve_scan_report(client: CxOneClient, exportId: str) -> requests.Response:
    """|LowLevelApiDocstring| Verb: GET Endpoint: /api/sca/export/requests/{exportId}/download

    .. deprecated:: 1.1.9
    Use: :func:`cxone_api.low.sca.export_service.download_a_report`
    
    """
    url = urljoin(client.api_endpoint, f"sca/export/requests/{exportId}/download")
    return await client.exec_request(requests.get, url)
