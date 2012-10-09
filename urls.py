from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    
    # url(r'^$', 'redokes.views.home', name='home'),
    # url(r'^redokes/', include('redokes.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

#This should always be last
urlpatterns.append(
    
    url(r'^(.*?)$', 'redokes.views.route')
)