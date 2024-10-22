import os, asyncio
from pathlib import Path
import cxone_api as cx
from cxone_api.util import json_on_ok
from cxone_api.low.uploads import generate_upload_link, upload_to_link
from cxone_api.high.scans import ScanInvoker
from cxone_api.high.projects import ProjectRepoConfig
from cxone_api.high.util import scan_inspector_factory
import cxone_api.low.projects as projects

# This example is intended to demonstrate the use of high-level APIs to
# invoke a scan.

# For this example, the following environment variables are used:
# TEST_OAUTH_CLIENT_ID - the client id of the OAuth client created in CheckmaxOne IAM
# TEST_OAUTH_CLIENT_SECRET - the client secret of the OAuth client created in CheckmaxOne IAM
# TEST_REGION - the name of the multi-tenant region for your test tenant.
# TEST_TENANT_ID - the name of the multi-tenant tenant

# Modify the following variables to suit your testing needs.
test_project_name = "example high-level api project"
example_zip_path = Path(os.path.dirname(os.path.realpath(__file__))) / Path("example.zip")

# Create an CxOne client using OAuth credentials.
oauth_client = cx.client.CxOneClient.create_with_oauth(os.environ['TEST_OAUTH_CLIENT_ID'], os.environ['TEST_OAUTH_CLIENT_SECRET'],
                "Example", 
                cx.AuthRegionEndpoints[os.environ['TEST_REGION']](os.environ['TEST_TENANT_ID']),
                cx.ApiRegionEndpoints[os.environ['TEST_REGION']]())

async def run_example():

    # See if the project exists first.  If an attempt is made to create an existing project,
    # the response will fail.  This method retrieves by name.
    project_list = json_on_ok(await projects.retrieve_list_of_projects(oauth_client, name=test_project_name))

    # The expected return is 0 or 1.
    if project_list['filteredTotalCount'] == 1:
        project_json = project_list['projects'][0]
    elif project_list['filteredTotalCount'] == 0:
        # Create a project, note that the passed dict follows the "body" content
        # in the CheckmarxOne REST API documentation.  This form uses the argument
        # unpacking operator (**) as an example of how the API POST body can be formed.
        # The returned "requests.Response" should contain JSON if the create is successful.
        project_json = json_on_ok(await projects.create_a_project(oauth_client, **{ "name" : test_project_name}))

        # An alternate example without the argument unpacking operator.
        # project = json_on_ok(await projects.create_a_project(oauth_client, name=test_project_name))

    else:
        print(f"Project list returned {project_list['filteredTotalCount']} projects, ending.")
        return

    scan_id = await ScanInvoker.scan_get_scanid(oauth_client, await ProjectRepoConfig.from_project_json(oauth_client, project_json), 
                                branch=None, engines=['sast', 'sca'], src_zip_path=example_zip_path)
                                                                                  
    print(f"Scan {scan_id} running.")
    
    scan_inspector = await scan_inspector_factory(oauth_client, scan_id)

    while scan_inspector.executing:
        # Wait 30 seconds to check again
        await asyncio.sleep(30)
        scan_inspector = await scan_inspector_factory(oauth_client, scan_id)
    
    print (f"Scan Id {scan_id} finished {"successfully" if scan_inspector.successful else f"with failure [{scan_inspector.state_msg}]" if scan_inspector.failed else "with unknown state"}.")


asyncio.run(run_example())


