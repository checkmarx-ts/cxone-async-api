import os, asyncio
import cxone_api as cx
from cxone_api.high.scan_configuration import ProjectScanConfiguration
from cxone_api.high.scan_configuration.categories import ConfigurationPropertyHandler

# This example shows how to set Project-level configurations.  These appear
# in project settings as "Rules".

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

async def make_prop_string(name : str, handler : ConfigurationPropertyHandler):
    note = "Can Override" if await handler.getOverride() else "No Override"
    return f"\t{name}={await handler.getValue()}({note})"

async def print_current(project_config : ProjectScanConfiguration):
    print("SAST Current Settings:")
    print(await make_prop_string("Fast Scan", project_config.SAST.FastScan))
    print(await make_prop_string("Engine Verbose", project_config.SAST.EngineVerbose))
    print(await make_prop_string("Exclusions", project_config.SAST.Exclusions))
    print(await make_prop_string("Incremental Scan", project_config.SAST.IncrementalScan))
    print(await make_prop_string("Language Mode", project_config.SAST.LanguageMode))
    print(await make_prop_string("Preset", project_config.SAST.Preset))
    print(await make_prop_string("Use Recommended Exclusions", project_config.SAST.RecommendedExclusions))

    print("SCA Current Settings:")
    print(await make_prop_string("Exploitable Path", project_config.SCA.ExploitablePath))
    print(await make_prop_string("Exploitable Path Last Scan Days", project_config.SCA.ExploitablePathLastScanDays))
    print(await make_prop_string("Exclusions", project_config.SCA.Exclusions))
    print(await make_prop_string("Obfuscate Packages Pattern", project_config.SCA.ObfuscatePackagesPattern))

    print("API Security Current Settings:")
    print(await make_prop_string("Swagger Filter", project_config.APISec.SwaggerFilter))
    
    print("Container Security Current Settings:")
    print(await make_prop_string("Exclude Non Final Stages Filter", project_config.Containers.ExclusionNonFinalStagesFilter))
    print(await make_prop_string("Exclusions", project_config.Containers.Exclusions))
    print(await make_prop_string("Image Tag Filter", project_config.Containers.ImageTagFilter))
    print(await make_prop_string("Private Package Filter", project_config.Containers.PrivatePackageFilter))

async def run_example():

    # Set your project ID in the string before running the sample.
    project_config = ProjectScanConfiguration(oauth_client, "c95a8ef1-31ee-43ad-9f25-d1726c5d1269")

    print ("BEFORE CHANGES:")
    await print_current(project_config)

    # Set and commit a setting.
    await project_config.SAST.FastScan.setValue(True)
    await project_config.SAST.FastScan.setOverride(False)
    await project_config.commit_config()

    print ("AFTER CHANGES:")
    await print_current(project_config)

    # Reset a setting to default
    await project_config.SAST.FastScan.reset()
    await project_config.SAST.FastScan.reset()
    await project_config.commit_config()

    print ("AFTER RESET:")
    await print_current(project_config)

asyncio.run(run_example())


