import os, asyncio
from pathlib import Path
import cxone_api as cx
from cxone_api.util import json_on_ok, page_generator
import cxone_api.low.projects as projects

# This example is intended to demonstrate the use of mostly low-level APIs to
# iterate the list of projects.  The list of projects returned is limited to
# 20 by default with a max of 100 per page.  The page_generator handles
# additional requests to the API as needed to load the next page.

# Modify the values of these variables as needed:
# Set the project list page size to 1 to cause multiple trips to the API
# to retrieve all projects
page_size = 1


# For this example, the following environment variables are used:
# TEST_OAUTH_CLIENT_ID - the client id of the OAuth client created in CheckmaxOne IAM
# TEST_OAUTH_CLIENT_SECRET - the client secret of the OAuth client created in CheckmaxOne IAM
# TEST_REGION - the name of the multi-tenant region for your test tenant.
# TEST_TENANT_ID - the name of the multi-tenant tenant

# Create an CxOne client using OAuth credentials.
oauth_client = cx.client.CxOneClient.create_with_oauth(os.environ['TEST_OAUTH_CLIENT_ID'], os.environ['TEST_OAUTH_CLIENT_SECRET'],
                "Example", 
                cx.AuthRegionEndpoints[os.environ['TEST_REGION']](os.environ['TEST_TENANT_ID']),
                cx.ApiRegionEndpoints[os.environ['TEST_REGION']]())

async def run_example():
    # The page_generator is given the API coroutine and the name of the root element in the response
    # that has the result objects.
    async for page in page_generator(projects.retrieve_list_of_projects, "projects", client=oauth_client, limit=page_size):
        print(page)

asyncio.run(run_example())


