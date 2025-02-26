import os, asyncio
import cxone_api as cx
from cxone_api.high.scan_configuration import TenantScanConfiguration
from cxone_api.high.scan_configuration.categories import ConfigurationPropertyHandler

# This example shows how to set Tenant-level configurations.
# WARNING: These configuration changes will affect scans in your tenant.  It is suggested
# to run this only on a test tenant.

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

async def print_current(tenant_config : TenantScanConfiguration):
    print("SAST Current Settings:")
    print(await make_prop_string("Fast Scan", tenant_config.SAST.FastScan))
    print(await make_prop_string("Engine Verbose", tenant_config.SAST.EngineVerbose))
    print(await make_prop_string("Exclusions", tenant_config.SAST.Exclusions))
    print(await make_prop_string("Incremental Scan", tenant_config.SAST.IncrementalScan))
    print(await make_prop_string("Language Mode", tenant_config.SAST.LanguageMode))
    print(await make_prop_string("Preset", tenant_config.SAST.Preset))
    print(await make_prop_string("Use Recommended Exclusions", tenant_config.SAST.RecommendedExclusions))

    print("SCA Current Settings:")
    print(await make_prop_string("Exploitable Path", tenant_config.SCA.ExploitablePath))
    print(await make_prop_string("Exploitable Path Last Scan Days", tenant_config.SCA.ExploitablePathLastScanDays))
    print(await make_prop_string("Exclusions", tenant_config.SCA.Exclusions))
    print(await make_prop_string("Obfuscate Packages Pattern", tenant_config.SCA.ObfuscatePackagesPattern))

    print("API Security Current Settings:")
    print(await make_prop_string("Swagger Filter", tenant_config.APISec.SwaggerFilter))
    
    print("Container Security Current Settings:")
    print(await make_prop_string("Exclude Non Final Stages Filter", tenant_config.Containers.ExclusionNonFinalStagesFilter))
    print(await make_prop_string("Exclusions", tenant_config.Containers.Exclusions))
    print(await make_prop_string("Image Tag Filter", tenant_config.Containers.ImageTagFilter))
    print(await make_prop_string("Private Package Filter", tenant_config.Containers.PrivatePackageFilter))

async def run_example():

    tenant_config = TenantScanConfiguration(oauth_client)

    print ("BEFORE CHANGES:")
    await print_current(tenant_config)

    # Set and commit a setting.
    await tenant_config.SAST.FastScan.setValue(True)
    await tenant_config.SAST.FastScan.setOverride(False)
    await tenant_config.commit_config()

    print ("AFTER CHANGES:")
    await print_current(tenant_config)

    # Reset a setting to default
    await tenant_config.SAST.FastScan.reset()
    await tenant_config.SAST.FastScan.reset()
    await tenant_config.commit_config()

    print ("AFTER RESET:")
    await print_current(tenant_config)

asyncio.run(run_example())


