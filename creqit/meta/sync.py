import creqit
from creqit import _
from creqit.meta.meta_client import MetaClient
from creqit.meta.doctype.meta_settings.meta_settings import MetaSettings
from creqit.utils import now_datetime

def sync_all(test_mode=False):
    """Sync all Meta data"""
    try:
        import sys
        def debug_print(msg):
            sys.stderr.write(f"{msg}\n")
            sys.stderr.flush()
            
        debug_print("Starting Meta sync...")
        settings = MetaSettings.get_settings()
        debug_print(f"Settings loaded: sync_enabled={settings.sync_enabled}")
        
        if not settings.sync_enabled:
            debug_print("Meta sync is disabled in settings")
            creqit.msgprint(_("Meta sync is disabled in settings"))
            return
            
        if not settings.access_token and not test_mode:
            debug_print("Meta access token is not configured")
            creqit.msgprint(_("Meta access token is not configured"))
            return
            
        debug_print("Updating sync status to In Progress")
        settings.update_sync_status("In Progress")
        
        if test_mode:
            debug_print("Running in test mode...")
            # Create test data
            create_test_data()
        else:
            debug_print("Creating Meta client...")
            client = MetaClient()
            
            try:
                # Sync campaigns
                debug_print("Starting campaign sync...")
                sync_campaigns(client)
                debug_print("Campaign sync completed")
                
                # Sync ad sets
                debug_print("Starting ad set sync...")
                try:
                    ad_sets = client.get_ad_sets()
                    debug_print(f"Ad sets response: {ad_sets}")
                    
                    if not ad_sets:
                        debug_print("No response from Meta API for ad sets")
                        creqit.msgprint(_("No response from Meta API for ad sets"))
                        return
                        
                    if not ad_sets.get("data"):
                        debug_print("No ad sets data in response")
                        creqit.msgprint(_("No ad sets found to sync"))
                        return
                        
                    for ad_set_data in ad_sets.get("data", []):
                        try:
                            ad_set_id = ad_set_data.get("id")
                            if not ad_set_id:
                                debug_print(f"Ad set data missing ID: {ad_set_data}")
                                continue
                                
                            debug_print(f"Processing ad set {ad_set_id}")
                            
                            # Check if ad set exists
                            existing = creqit.get_all("Meta Ad Set", filters={"meta_ad_set_id": ad_set_id})
                            debug_print(f"Existing ad set: {existing}")
                            
                            # Create base ad set document without targeting_countries
                            ad_set_doc = {
                                "doctype": "Meta Ad Set",
                                "ad_set_id": ad_set_data.get("name"),
                                "ad_set_name": ad_set_data.get("name"),
                                "ad_set_status": ad_set_data.get("status", "Active"),
                                "meta_ad_set_id": ad_set_id,
                                "meta_campaign_id": ad_set_data.get("campaign_id"),
                                "meta_account_id": ad_set_data.get("account_id")
                            }
                            
                            # Add targeting data
                            targeting = ad_set_data.get("targeting", {})
                            debug_print(f"Targeting data for ad set {ad_set_id}: {targeting}")
                            
                            if targeting:
                                ad_set_doc["targeting_age_min"] = targeting.get("age_min", 18)
                                ad_set_doc["targeting_age_max"] = targeting.get("age_max", 65)
                                
                                # Handle gender values
                                genders = targeting.get("genders", [])
                                if isinstance(genders, list):
                                    if 1 in genders and 2 not in genders:
                                        ad_set_doc["targeting_genders"] = "Male"
                                    elif 2 in genders and 1 not in genders:
                                        ad_set_doc["targeting_genders"] = "Female"
                                    else:
                                        ad_set_doc["targeting_genders"] = "All"
                                else:
                                    ad_set_doc["targeting_genders"] = "All"
                            
                            debug_print(f"Base ad set doc for {ad_set_id}: {ad_set_doc}")
                            
                            # Create or update the document
                            if existing:
                                # Update existing ad set
                                doc = creqit.get_doc("Meta Ad Set", existing[0].name)
                                doc.update(ad_set_doc)
                                doc.save()
                            else:
                                # Create new ad set
                                doc = creqit.get_doc(ad_set_doc)
                                doc.insert()
                            
                            # Now handle targeting_countries separately
                            try:
                                if targeting and targeting.get("geo_locations", {}).get("countries"):
                                    countries = targeting["geo_locations"]["countries"]
                                    debug_print(f"Countries data for ad set {ad_set_id}: {countries}")
                                    
                                    # Get the document again to ensure we have the latest version
                                    doc = creqit.get_doc("Meta Ad Set", doc.name)
                                    
                                    # Clear existing countries
                                    doc.set("targeting_countries", [])
                                    
                                    # Add new countries
                                    for country_code in countries:
                                        if isinstance(country_code, str):
                                            doc.append("targeting_countries", {
                                                "country_code": country_code,
                                                "country_name": country_code
                                            })
                                    
                                    doc.save()
                            except Exception as e:
                                import traceback
                                error_details = traceback.format_exc()
                                debug_print(f"Error handling targeting_countries for ad set {ad_set_id}: {str(e)}")
                                debug_print(f"Error details:\n{error_details}")
                                # Continue with other ad sets even if this one fails
                                
                        except Exception as e:
                            import traceback
                            error_details = traceback.format_exc()
                            debug_print(f"Error syncing ad set {ad_set_id}: {str(e)}")
                            debug_print(f"Ad Set Data: {ad_set_data}")
                            debug_print(f"Error details:\n{error_details}")
                            # Continue with other ad sets even if this one fails
                            
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    debug_print(f"Error in sync_ad_sets: {str(e)}")
                    debug_print(f"Error details:\n{error_details}")
                    raise
                
                debug_print("Ad set sync completed")
                
                # Sync ads
                debug_print("Starting ad sync...")
                sync_ads(client)
                debug_print("Ad sync completed")
                
                # Sync leads
                debug_print("Starting lead sync...")
                sync_leads(client)
                debug_print("Lead sync completed")
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                debug_print(f"Error during sync: {str(e)}")
                debug_print(f"Error details:\n{error_details}")
                raise
        
        # Update last sync time and status
        debug_print("Updating sync status to Completed")
        settings.update_sync_status("Completed")
        creqit.msgprint(_("Meta sync completed successfully"))
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        debug_print(f"Error in sync_all: {str(e)}")
        debug_print(f"Error details:\n{error_details}")
        settings.update_sync_status("Failed", str(e))
        raise

def create_test_data():
    """Create test data for Meta integration"""
    try:
        # Create test campaign
        campaign_doc = {
            "doctype": "Meta Campaign",
            "campaign_id": "TEST_CAMPAIGN_001",
            "campaign_name": "Test Campaign",
            "campaign_status": "Active",
            "campaign_objective": "LEAD_GENERATION",
            "meta_campaign_id": "123456789",
            "meta_account_id": "987654321"
        }
        
        campaign = creqit.get_doc(campaign_doc)
        campaign.insert()
        
        # Create test ad set
        ad_set_doc = {
            "doctype": "Meta Ad Set",
            "ad_set_id": "TEST_ADSET_001",
            "ad_set_name": "Test Ad Set",
            "ad_set_status": "Active",
            "meta_ad_set_id": "234567890",
            "meta_campaign_id": "123456789",
            "meta_account_id": "987654321",
            "targeting_age_min": 18,
            "targeting_age_max": 65,
            "targeting_genders": "All",
            "targeting_countries": [
                {
                    "doctype": "Meta Country",
                    "country_code": "TR",
                    "country_name": "Turkey"
                },
                {
                    "doctype": "Meta Country",
                    "country_code": "US",
                    "country_name": "United States"
                }
            ]
        }
        
        ad_set = creqit.get_doc(ad_set_doc)
        ad_set.insert()
        
        # Create test ad
        ad_doc = {
            "doctype": "Meta Ad",
            "ad_id": "TEST_AD_001",
            "ad_name": "Test Ad",
            "ad_status": "Active",
            "meta_ad_id": "345678901",
            "meta_ad_set_id": "234567890",
            "meta_campaign_id": "123456789",
            "meta_account_id": "987654321",
            "creative_type": "Image",
            "creative_title": "Test Ad Title",
            "creative_body": "Test Ad Body",
            "creative_image_url": "https://example.com/test-image.jpg"
        }
        
        ad = creqit.get_doc(ad_doc)
        ad.insert()
        
        # Create test lead
        lead_doc = {
            "doctype": "Meta Lead",
            "lead_id": "TEST_LEAD_001",
            "lead_name": "Test Lead",
            "lead_email": "test@example.com",
            "lead_phone": "+901234567890",
            "lead_status": "New",
            "meta_lead_id": "456789012",
            "meta_ad_id": "345678901",
            "meta_ad_set_id": "234567890",
            "meta_campaign_id": "123456789",
            "meta_account_id": "987654321"
        }
        
        lead = creqit.get_doc(lead_doc)
        lead.insert()
        
        creqit.msgprint(_("Test data created successfully"))
        
    except Exception as e:
        creqit.log_error("Error creating test data", str(e))
        raise

def sync_campaigns(client):
    """Sync campaigns from Meta"""
    campaigns = client.get_campaigns()
    
    if not campaigns or not campaigns.get("data"):
        creqit.msgprint(_("No campaigns found to sync"))
        return
        
    for campaign_data in campaigns.get("data", []):
        try:
            campaign_id = campaign_data.get("id")
            if not campaign_id:
                continue
                
            # Check if campaign exists
            existing = creqit.get_all("Meta Campaign", filters={"meta_campaign_id": campaign_id})
            
            campaign_doc = {
                "doctype": "Meta Campaign",
                "campaign_id": campaign_data.get("name"),
                "campaign_name": campaign_data.get("name"),
                "campaign_status": campaign_data.get("status"),
                "campaign_objective": campaign_data.get("objective"),
                "meta_campaign_id": campaign_id,
                "meta_account_id": campaign_data.get("account_id")
            }
            
            if existing:
                # Update existing campaign
                doc = creqit.get_doc("Meta Campaign", existing[0].name)
                doc.update(campaign_doc)
                doc.save()
            else:
                # Create new campaign
                doc = creqit.get_doc(campaign_doc)
                doc.insert()
                
        except Exception as e:
            creqit.log_error(f"Error syncing campaign {campaign_id}", str(e))
            
def sync_ad_sets(client):
    """Sync ad sets from Meta"""
    try:
        creqit.log_error("Getting ad sets from Meta API", "Debug info")
        ad_sets = client.get_ad_sets()
        creqit.log_error("Ad sets response", str(ad_sets))
        
        if not ad_sets:
            creqit.log_error("Meta API Error", "No response from Meta API for ad sets")
            creqit.msgprint(_("No response from Meta API for ad sets"))
            return
            
        if not ad_sets.get("data"):
            creqit.log_error("Meta API Error", "No ad sets data in response")
            creqit.msgprint(_("No ad sets found to sync"))
            return
            
        for ad_set_data in ad_sets.get("data", []):
            try:
                ad_set_id = ad_set_data.get("id")
                if not ad_set_id:
                    creqit.log_error("Meta API Error", f"Ad set data missing ID: {ad_set_data}")
                    continue
                    
                creqit.log_error(f"Processing ad set {ad_set_id}", "Debug info")
                
                # Check if ad set exists
                existing = creqit.get_all("Meta Ad Set", filters={"meta_ad_set_id": ad_set_id})
                
                # Create base ad set document without targeting_countries
                ad_set_doc = {
                    "doctype": "Meta Ad Set",
                    "ad_set_id": ad_set_data.get("name"),
                    "ad_set_name": ad_set_data.get("name"),
                    "ad_set_status": ad_set_data.get("status", "Active"),
                    "meta_ad_set_id": ad_set_id,
                    "meta_campaign_id": ad_set_data.get("campaign_id"),
                    "meta_account_id": ad_set_data.get("account_id")
                }
                
                # Add targeting data
                targeting = ad_set_data.get("targeting", {})
                creqit.log_error(f"Targeting data for ad set {ad_set_id}", str(targeting))
                
                if targeting:
                    ad_set_doc["targeting_age_min"] = targeting.get("age_min", 18)
                    ad_set_doc["targeting_age_max"] = targeting.get("age_max", 65)
                    
                    # Handle gender values
                    genders = targeting.get("genders", [])
                    if isinstance(genders, list):
                        if 1 in genders and 2 not in genders:
                            ad_set_doc["targeting_genders"] = "Male"
                        elif 2 in genders and 1 not in genders:
                            ad_set_doc["targeting_genders"] = "Female"
                        else:
                            ad_set_doc["targeting_genders"] = "All"
                    else:
                        ad_set_doc["targeting_genders"] = "All"
                
                creqit.log_error(f"Base ad set doc for {ad_set_id}", str(ad_set_doc))
                
                # Create or update the document
                if existing:
                    # Update existing ad set
                    doc = creqit.get_doc("Meta Ad Set", existing[0].name)
                    doc.update(ad_set_doc)
                    doc.save()
                else:
                    # Create new ad set
                    doc = creqit.get_doc(ad_set_doc)
                    doc.insert()
                
                # Now handle targeting_countries separately
                try:
                    if targeting and targeting.get("geo_locations", {}).get("countries"):
                        countries = targeting["geo_locations"]["countries"]
                        creqit.log_error(f"Countries data for ad set {ad_set_id}", str(countries))
                        
                        # Get the document again to ensure we have the latest version
                        doc = creqit.get_doc("Meta Ad Set", doc.name)
                        
                        # Clear existing countries
                        doc.set("targeting_countries", [])
                        
                        # Add new countries
                        for country_code in countries:
                            if isinstance(country_code, str):
                                doc.append("targeting_countries", {
                                    "country_code": country_code,
                                    "country_name": country_code
                                })
                        
                        doc.save()
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    creqit.log_error(f"Error handling targeting_countries for ad set {ad_set_id}", str(e))
                    creqit.log_error("Detailed error traceback", error_details)
                    # Continue with other ad sets even if this one fails
                    
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                creqit.log_error(f"Error syncing ad set {ad_set_id}", str(e))
                creqit.log_error("Ad Set Data", str(ad_set_data))
                creqit.log_error("Detailed error traceback", error_details)
                # Continue with other ad sets even if this one fails
                
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        creqit.log_error("Error in sync_ad_sets", str(e))
        creqit.log_error("Detailed error traceback", error_details)
        raise
            
def sync_ads(client):
    """Sync ads from Meta"""
    ads = client.get_ads()
    
    if not ads or not ads.get("data"):
        creqit.msgprint(_("No ads found to sync"))
        return
        
    for ad_data in ads.get("data", []):
        try:
            ad_id = ad_data.get("id")
            if not ad_id:
                continue
                
            # Check if ad exists
            existing = creqit.get_all("Meta Ad", filters={"meta_ad_id": ad_id})
            
            ad_doc = {
                "doctype": "Meta Ad",
                "ad_id": ad_data.get("name"),
                "ad_name": ad_data.get("name"),
                "ad_status": ad_data.get("status"),
                "meta_ad_id": ad_id,
                "meta_ad_set_id": ad_data.get("adset_id"),
                "meta_campaign_id": ad_data.get("campaign_id"),
                "meta_account_id": ad_data.get("account_id")
            }
            
            # Add creative data
            creative = ad_data.get("creative", {})
            if creative:
                ad_doc["creative_type"] = creative.get("type", "Image")
                ad_doc["creative_title"] = creative.get("title")
                ad_doc["creative_body"] = creative.get("body")
                
                if ad_doc["creative_type"] == "Image":
                    ad_doc["creative_image_url"] = creative.get("image_url")
                else:
                    ad_doc["creative_video_url"] = creative.get("video_url")
            
            if existing:
                # Update existing ad
                doc = creqit.get_doc("Meta Ad", existing[0].name)
                doc.update(ad_doc)
                doc.save()
            else:
                # Create new ad
                doc = creqit.get_doc(ad_doc)
                doc.insert()
                
        except Exception as e:
            creqit.log_error(f"Error syncing ad {ad_id}", str(e))
            
def sync_leads(client):
    """Sync leads from Meta"""
    leads = client.get_leads()
    
    if not leads or not leads.get("data"):
        creqit.msgprint(_("No leads found to sync"))
        return
        
    for lead_data in leads.get("data", []):
        try:
            lead_id = lead_data.get("id")
            if not lead_id:
                continue
                
            # Check if lead exists
            existing = creqit.get_all("Meta Lead", filters={"meta_lead_id": lead_id})
            
            lead_doc = {
                "doctype": "Meta Lead",
                "lead_id": lead_data.get("name"),
                "lead_name": lead_data.get("name"),
                "lead_email": lead_data.get("email"),
                "lead_phone": lead_data.get("phone"),
                "lead_status": lead_data.get("status", "New"),
                "meta_lead_id": lead_id,
                "meta_ad_id": lead_data.get("ad_id"),
                "meta_ad_set_id": lead_data.get("adset_id"),
                "meta_campaign_id": lead_data.get("campaign_id"),
                "meta_account_id": lead_data.get("account_id")
            }
            
            if existing:
                # Update existing lead
                doc = creqit.get_doc("Meta Lead", existing[0].name)
                doc.update(lead_doc)
                doc.save()
            else:
                # Create new lead
                doc = creqit.get_doc(lead_doc)
                doc.insert()
                
        except Exception as e:
            creqit.log_error(f"Error syncing lead {lead_id}", str(e)) 