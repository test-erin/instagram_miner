from django.conf.urls import url
from . import views

urlpatterns = [
	# Home page shows a list of campaigns already created
    url(r'^$', views.campaign_list, name='campaign_list'),

    # Campaign detail page shows results of campaign-specific search
    url(r'^campaign/(?P<pk>\d+)/$', views.campaign_detail, name='campaign_detail'),

    # New campaign page lets a user create a new campaign
    url(r'^campaign/new/$', views.new_campaign, name='new_campaign'),
]