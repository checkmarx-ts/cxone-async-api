import requests
from requests.compat import urljoin
from ..client import CxOneClient
from ..util import dashargs, join_query_dict


@dashargs(
        "apply-predicates",
        "first-found-at",
        "first-found-at-operation",
        "notes-operation",
        "number-of-nodes",
        "number-of-nodes-operation",
        "preset-id",
        "query-ids",
        "result-ids",
        "sink-file",
        "sink-file-operation",
        "sink-line",
        "sink-line-operation",
        "sink-node",
        "sink-node-operation",
        "source-file",
        "source-file-operation",
        "source-line",
        "source-line-operation",
        "source-node",
        "source-node-operation",
        "group-by-field",
        "scan-id")
async def retrieve_aggregated_summary_of_sast_results(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "sast-scan-summary/aggregate")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

@dashargs(
        "query-ids",
        "base-scan-id",
        "group-by-field",
        "scan-id")
async def retrieve_aggregated_summary_of_sast_results_comparison(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "sast-scan-summary/compare/aggregate")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)
