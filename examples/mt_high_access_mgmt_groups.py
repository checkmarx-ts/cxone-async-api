import os, asyncio
import cxone_api as cx
from cxone_api.high.access_mgmt.user_mgmt import Groups

# This example is intended to demonstrate the use of high-level APIs to
# retrieve a list of projects by group membership.

# For this example, the following environment variables are used:
# TEST_OAUTH_CLIENT_ID - the client id of the OAuth client created in CheckmaxOne IAM
# TEST_OAUTH_CLIENT_SECRET - the client secret of the OAuth client created in CheckmaxOne IAM
# TEST_REGION - the name of the multi-tenant region for your test tenant.
# TEST_TENANT_ID - the name of the multi-tenant tenant

# The client must have the IAM role required to manage groups for this to work.

# Create an CxOne client using OAuth credentials.
oauth_client = cx.client.CxOneClient.create_with_oauth(os.environ['TEST_OAUTH_CLIENT_ID'], os.environ['TEST_OAUTH_CLIENT_SECRET'],
                "Example", 
                cx.AuthRegionEndpoints[os.environ['TEST_REGION']](os.environ['TEST_TENANT_ID']),
                cx.ApiRegionEndpoints[os.environ['TEST_REGION']]())

async def run_example():
  g = Groups(oauth_client)
  print("Project IDs by group membership:")
  for path in await g.get_path_list():
    print(path + ":")
    group_desc = await g.get_by_full_path(path)
    for proj in await g.get_project_ids_by_groups([group_desc]):
      print(f"\t{proj}")

asyncio.run(run_example())


