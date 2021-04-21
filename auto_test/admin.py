from django.contrib import admin

# Register your models here.
from .import models

admin.site.register(models.Project,models.ProjectAdmin)
admin.site.register(models.Module,models.ModuleAdmin)
admin.site.register(models.TestCase,models.TestCaseAdmin)
admin.site.register(models.TestSuit,models.TestSuitAdmin)
admin.site.register(models.Configuration,models.ConfigurationAdmin)


