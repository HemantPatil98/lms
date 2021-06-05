from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import user_profile
# Register your models here.
admin.site.register(Permission)
admin.site.site_header = 'Cravita Technologies'                    # default: "Django Administration"
admin.site.index_title = 'Learning Managment System'                 # default: "Site administration"
admin.site.site_title = 'Learning Managment System'

admin.site.register(user_profile)