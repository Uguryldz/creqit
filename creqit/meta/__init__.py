from __future__ import unicode_literals

__version__ = '0.0.1'

import creqit
from creqit import _

def get_meta_settings():
    return creqit.get_doc("Meta Settings", "Meta Settings")

# Import all modules
from . import meta_client
from . import sync
from . import webhook
from . import report
from . import scheduler
