import os
from logging import getLogger

import pandas as pd

from django.conf import settings
from django.core.management.base import BaseCommand

from requirements.applogic.import_source_table import import_source_table

log = getLogger("django")


class Command(BaseCommand):
    help = """
        Import Source data table to database
    """

    def handle(self, *args, **kwargs):
        try:
            df = pd.read_excel(
                os.path.join(settings.STATICFILES_DIRS[0], "data/CRS_03Oct23.xlsm"),
                sheet_name="Source Table",
            )
            import_source_table(df)
            log.info("Successfully imported source table.")
        except Exception as err:
            log.error(err)
