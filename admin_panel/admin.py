from django.contrib import admin
from django.http import HttpResponse,Http404
from django.http import HttpResponse
from django.urls import path
from .models import *
from django.contrib.admin import AdminSite,ModelAdmin
from django.utils.html import format_html

# Register your models here.
from .models import *
admin.site.register(BookingHistoryMachine)



# # class CustomAdminSite(admin.AdminSite):
# #     site_header = 'My Custom Admin'
# #     site_title = 'My Custom Admin'
# #     index_title = 'Dashboard'

# #     def get_urls(self):
# #         urls = super().get_urls()
# #         custom_urls = [
# #             path('custom/', custom_admin),
# #         ]
# #         return custom_urls + urls

# #     def admin_view(self, view, cacheable=False):
# #         def inner(request, *args, **kwargs):
# #             if request.path.startswith('/admin/custom'):
# #                 return view(request, *args, **kwargs)
# #             else:
# #                 raise Http404('Invalid admin URL')
# #         return super().admin_view(inner, cacheable)

# # admin_site = CustomAdminSite()


# # class Home2ModelAdmin(ModelAdmin):
# #     def get_urls(self):
# #         urls = super().get_urls()
# #         custom_urls = [
# #             path('home2/', home2, name='home2'),
# #         ]
# #         return custom_urls + urls

# # class CustomAdminSite(AdminSite):
# #     site_header = 'My Custom Admin Site'
# #     site_title = 'My Custom Admin Site'

# # custom_admin_site = CustomAdminSite(name='mycustomadmin')
# # custom_admin_site.register(Home2ModelAdmin)
# from django.shortcuts import render
# class CustomAdminView(ModelAdmin):
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('custom_home/', self.admin_site.admin_view(self.custom_home_view), name='custom_home'),
#         ]
#         return custom_urls + urls

#     def custom_home_view(self, request):
#         # Your view logic goes here
#         # For example, render the custom_home.html template
#         context = {}
#         return render(request, 'admin/custom_home.html', context)
from .views import my_custom_view

class MyModelAdmin(admin.ModelAdmin):
    # ... your other ModelAdmin code ...

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom/', my_custom_view, name='admin_custom'),
        ]
        print(custom_urls)
        return custom_urls + urls
    
admin.site.register(BookingHistorySahayak)

