import os, asyncio
import cxone_api as cx
from cxone_api.high.scan_configuration import ScanConfiguration
from cxone_api.high.scan_configuration.categories import ConfigurationPropertyHandler

# This example shows how to read a scan configuration.  Scan configuration values
# are read-only, so attempting to change a configuration will throw an
# exception.

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

async def print_current(scan_config : ScanConfiguration):
    print("SAST Current Settings:")
    print(await make_prop_string("Fast Scan", scan_config.SAST.FastScan))
    print(await make_prop_string("Engine Verbose", scan_config.SAST.EngineVerbose))
    print(await make_prop_string("Exclusions", scan_config.SAST.Exclusions))
    print(await make_prop_string("Incremental Scan", scan_config.SAST.IncrementalScan))
    print(await make_prop_string("Language Mode", scan_config.SAST.LanguageMode))
    print(await make_prop_string("Preset", scan_config.SAST.Preset))
    print(await make_prop_string("Use Recommended Exclusions", scan_config.SAST.RecommendedExclusions))

    print("SCA Current Settings:")
    print(await make_prop_string("Exploitable Path", scan_config.SCA.ExploitablePath))
    print(await make_prop_string("Exploitable Path Last Scan Days", scan_config.SCA.ExploitablePathLastScanDays))
    print(await make_prop_string("Exclusions", scan_config.SCA.Exclusions))
    print(await make_prop_string("Obfuscate Packages Pattern", scan_config.SCA.ObfuscatePackagesPattern))

    print("API Security Current Settings:")
    print(await make_prop_string("Swagger Filter", scan_config.APISec.SwaggerFilter))
    
    print("Container Security Current Settings:")
    print(await make_prop_string("Exclude Non Final Stages Filter", scan_config.Containers.ExclusionNonFinalStagesFilter))
    print(await make_prop_string("Exclusions", scan_config.Containers.Exclusions))
    print(await make_prop_string("Image Tag Filter", scan_config.Containers.ImageTagFilter))
    print(await make_prop_string("Private Package Filter", scan_config.Containers.PrivatePackageFilter))

async def run_example():

    # Set your project ID and scan ID in the string before running the sample.
    project_config = ScanConfiguration(oauth_client, project_id="c95a8ef1-31ee-43ad-9f25-d1726c5d1269", scan_id="7a22cd30-3f59-4730-a7c9-6e7abbac3edd")
    await print_current(project_config)

asyncio.run(run_example())


