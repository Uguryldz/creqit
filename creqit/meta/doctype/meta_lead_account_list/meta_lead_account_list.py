# Copyright (c) 2025, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit import _
from creqit.model.document import Document
from creqit.utils import now_datetime
import json


class MetaLeadAccountList(Document):
    """Single DocType that holds Facebook Pages in JSON and renders HTML"""
    pass


@creqit.whitelist()
def sync_accounts():
    """Sync Facebook Pages via Graph API v24.0 using access token from settings.
    Upsert records by page_id into Meta Lead Account List.
    """
    # Get access token from settings
    settings = creqit.get_doc('Facebook Lead Ads Settings', 'Facebook Lead Ads Settings')
    access_token = getattr(settings, 'access_token', None)
    if not access_token:
        creqit.throw(_('Access Token bulunamadı. Lütfen Facebook Lead Ads Settings sayfasından token girin.'))

    from creqit.meta.FacebookLeadAds.utils import make_facebook_request

    endpoint = '/me/accounts'
    params = {
        'fields': 'id,name,category,category_list,business,global_brand_page_name,location,tasks,access_token'
    }

    total = 0
    failures = 0
    after = None
    last_error = None
    all_accounts = []

    while True:
        if after:
            params['after'] = after
        try:
            resp = make_facebook_request(endpoint, access_token, params=params)
        except Exception as e:
            last_error = str(e)
            failures += 1
            break

        data = resp.get('data', []) or []
        for item in data:
            total += 1
            try:
                page_id = item.get('id')
                row_values = {
                    'page_id': page_id,
                    'page_name': item.get('name'),
                    'global_brand_page_name': item.get('global_brand_page_name'),
                    'category': item.get('category'),
                    'business_id': (item.get('business') or {}).get('id'),
                    'business_name': (item.get('business') or {}).get('name'),
                    'city': (item.get('location') or {}).get('city'),
                    'country': (item.get('location') or {}).get('country'),
                    'latitude': (item.get('location') or {}).get('latitude'),
                    'longitude': (item.get('location') or {}).get('longitude'),
                    'street': (item.get('location') or {}).get('street'),
                    'zip': (item.get('location') or {}).get('zip'),
                    'tasks': item.get('tasks') or [],
                    'page_access_token': item.get('access_token'),
                    'is_active': 1
                }
                all_accounts.append(row_values)
            except Exception as e:
                failures += 1
                last_error = str(e)

        paging = resp.get('paging') or {}
        cursors = paging.get('cursors') or {}
        after = cursors.get('after')
        if not after:
            break

    # Save once after paging done
    try:
        parent = creqit.get_doc('Meta Lead Account List')
        parent.accounts_json = json.dumps(all_accounts)
        current_ts = now_datetime()
        parent.last_synced_at = current_ts
        parent.save(ignore_permissions=True)
    except Exception:
        pass

    return {
        'total_processed': total,
        'failures': failures,
        'last_error': last_error
    }


