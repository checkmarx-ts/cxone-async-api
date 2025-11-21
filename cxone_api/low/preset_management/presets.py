import requests
from typing import Dict
from requests.compat import urljoin
from cxone_api.util import dashargs, join_query_dict
from cxone_api.client import CxOneClient


@dashargs("exact-match", "include-details", "search-term")
async def retrieve_list_of_presets(client : CxOneClient, scanner : str, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"preset-manager/{scanner}/presets")
    url = join_query_dict(url, kwargs)    
    return await client.exec_request(requests.get, url)

async def create_a_new_preset(client : CxOneClient, scanner : str, data : Dict) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"preset-manager/{scanner}/presets")
    return await client.exec_request(requests.post, url, json=data)

async def retrieve_list_of_queries_in_a_preset(client : CxOneClient, scanner : str, preset_id : str) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"preset-manager/{scanner}/presets/{preset_id}")
    return await client.exec_request(requests.get, url)

async def update_a_preset(client : CxOneClient, scanner : str, preset_id : str, data : Dict) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"preset-manager/{scanner}/presets/{preset_id}")
    return await client.exec_request(requests.put, url, json=data)

async def delete_a_preset_by_id(client : CxOneClient, scanner : str, preset_id : str) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"preset-manager/{scanner}/presets/{preset_id}")
    return await client.exec_request(requests.delete, url)

async def clone_a_preset(client : CxOneClient, scanner : str, preset_id : str, data : Dict) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"preset-manager/{scanner}/presets/{preset_id}/clone")
    return await client.exec_request(requests.post, url, json=data)
