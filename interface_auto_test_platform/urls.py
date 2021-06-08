"""interface_auto_test_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from auto_test import views

urlpatterns = [
    url('admin/', admin.site.urls),
    url('^index/$', views.index),
    url('^project/$', views.project, name="project"),
    url(r"^module/$", views.module, name="module"),
    url(r"^testcase/$", views.testcase, name="testcase"),
    url(r"^testrecord/$", views.testrecord, name="testrecord"),
    url(r"^moduleTestCases/(?P<module_id>[0-9]+)/$", views.module_testcases, name="moduleCases"),
    url(r"^testCaseDetail/(?P<testcase_id>[0-9]+)$", views.test_case_detail, name="testCaseDetail"),
    url(r'^testsuit/', views.testsuit, name="testsuit"),
    url(r'^suitcases/(?P<suit_id>[0-9]+)$', views.show_testsuit_cases, name="suitcases"),
    url(r"^testrecord/$", views.testrecord, name="testrecord"),
    url(r"^diffCaseResponse/(?P<test_record_id>[0-9]+)$$", views.diffCaseResponse, name="diffCaseResponse"),
    url(r"^diffSuiteCaseResponse/(?P<suite_case_record_id>[0-9]+)$$", views.diffSuiteCaseResponse, name="diffSuiteCaseResponse"),
    url(r'^testsuitrecord/$', views.show_test_suit_record, name="showsuitrecord"),
    url(r'^testcaserecord/(?P<suit_record_id>[0-9]+)$', views.show_test_suit_test_case_record, name="showsuitcaserecord"),
    url(r'^managesuit/(?P<suit_id>[0-9]+)$', views.managesuit, name="managesuit"),
    url(r'^testsuitstatistics/(?P<suit_id>[0-9]+)$',views.test_suit_statistics,name="testsuitstatistics"),
    url(r'^projectstatistics/(?P<project_id>[0-9]+)$', views.show_project_statistics, name="projectstatistics"),
    url(r'^modulestatistics/(?P<module_id>[0-9]+)$', views.show_module_statistics, name="testmodulestatistics"),
    url(r"^exceptioninfo/(?P<execute_id>[0-9]+)$", views.show_exception, name="showexception"),
    url('^login/$', views.login),
    url('^logout/$', views.logout),
    url('^accounts', views.login)

]
