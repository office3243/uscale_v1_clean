from django.contrib import admin
from django.conf import settings


admin.site.site_title = settings.BRANCH_NAME + " Administration"
admin.site.site_header = settings.BRANCH_NAME + " Administration"
