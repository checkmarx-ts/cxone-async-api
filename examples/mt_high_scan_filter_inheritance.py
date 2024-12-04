import os, asyncio
from pathlib import Path
from cxone_api.util import page_generator
import cxone_api as cx
import cxone_api.low.projects as projects
from cxone_api.high.projects import ProjectRepoConfig
from cxone_api.high.scans import ScanFilterConfig

# This example shows how to get file filters by engine that work through
# "inheriting" global filters with filters set at the project level.

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
    async for project in page_generator(projects.retrieve_list_of_projects, "projects", client=oauth_client):
        # Repo config gets the settings for the repository associated with the project, if any.
        repo_config = await ProjectRepoConfig.from_project_json(oauth_client, project)

        # Projects generated from code repository imports will have an SCM ID, otherwise the project will not have an SCM ID
        print(f"Project ID: {repo_config.project_id} Name: [{repo_config.name}] Repo URL: [{await repo_config.repo_url}] with scm id: {await repo_config.scm_id} Imported: {await repo_config.is_scm_imported}")

        # Filters are defined per engine and can be defined globally or at the project level.  The UI places the global config
        # in the project setting field but it is up to the user to add it.  If the project is configured to include the global
        # setting, it is up to a user to update the excludes if the global settings change.
        #
        # ScanFilterConfig will combine global and project along with optional additional filters.  This can be used
        # when submitting the scan.  If "Allow Override" is un-checked on any level, filters sent with the scan
        # request are ignored.
        filters = await ScanFilterConfig.from_repo_config(oauth_client, repo_config)
        print(f"\tEngines configured with filters: {",".join(filters.engines_with_filters)}")
        for engine in filters.engines_with_filters:
            print(f"\t\t{engine}: {filters.compute_filters(engine, "!**/my/additional/filter")}")

asyncio.run(run_example())


