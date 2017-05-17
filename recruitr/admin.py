from django.contrib.admin import AdminSite


class RecruitrAdminSite(AdminSite):
    site_header = 'Recruitr Administration'


admin_site = RecruitrAdminSite()
