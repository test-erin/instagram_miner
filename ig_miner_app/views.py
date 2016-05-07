from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import Lower
from .models import Campaign, Photo
from .forms import PostForm
from django import forms
import os
import requests
import time
import simplejson

def campaign_list(request):
    '''Renders a template showing a list of registered campaigns, sorted in alphabetical order.
    Campaigns are created by the user, who provides a hashtag and time range in which to search.'''

	campaigns = Campaign.objects.order_by(Lower('Campaign_Title').asc())
	    
	return render(request, 'ig_miner_app/campaign_list.html', {'campaigns': campaigns})


def campaign_detail(request, pk):
    ''' Renders a template showing the photo results of the campaign. 20 results per page,
    with pagination capabilities at the bottom of each page.''' 

    campaign = get_object_or_404(Campaign, pk=pk)

    # Query the DB to find all Photo records associated with this campaign
    results = Photo.objects.filter(campaign_number=pk)
    
    # Set up the pagination of the results
    paginator = Paginator(results, 20) # Show 20 contacts per page
    page = request.GET.get('page')

    try:
        page_content = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_content = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_content = paginator.page(paginator.num_pages)

    return render(request, 'ig_miner_app/campaign_detail.html', {'campaign': campaign,
                                                                'results':results,
                                                                'page_content': page_content})


def new_campaign(request):
    ''' Renders a template showing a form, based on the Campaign model, with which the user
    creates a new campaign. User provides a title, time range and hashtag.'''
    
    # Allow user to create a new campaign using a form
    if request.method == "POST":
        form = PostForm(request.POST)
        # Need code to force a user to provide an end date
        if form.is_valid():
            campaign = form.save()

            # Initialize variables (most pulled from form) for use in Instagram API call
            ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
            campaign_title=campaign.Campaign_Title
            hashtag = campaign.Hashtag
            pattern = '%m/%d/%Y'
            start_date = int(time.mktime(time.strptime(campaign.Start_Date, pattern)))
            end_date = int(time.mktime(time.strptime(campaign.End_Date, pattern)))
            url = "https://api.instagram.com/v1/tags/%s/media/recent?access_token=%s" % (hashtag, ACCESS_TOKEN)
            headers = {'count': 100}

            # Rate limit for this endpoint is 5000/hour
            contine_API_calls = True
            api_hit_count = 0
            
            while contine_API_calls:
                r = requests.get(url, headers=headers)
                jdict = r.json()
                data = jdict['data']
                pagination = jdict['pagination']

                # If retrieved photo falls within time range, add to DB
                for each in data:
                    post_date_epoch = int(each['created_time'])

                    if (post_date_epoch < end_date) and (post_date_epoch >= start_date) and (each['type'] == 'image' or 'Image'):
	                    created_date = post_date_epoch
	                    img_url = str(each['images']['low_resolution']['url'])
	                    post_link = str(each['link'])
	                    img_owner = str(each['user']['username'])

	                    new_Photo_record = Photo(hashtag=hashtag,
	                    	                     img_url=img_url,
	                    	                     img_owner=img_owner,
	                    	                     post_link=post_link,
	                    	                     pub_date=created_date,
                                                 campaign_number=campaign.id)
	                    new_Photo_record.save()

                # If the endpoint still contains data, retrieve it. Otherwise, stop.
                if 'next_url' in pagination:
            	    url = pagination['next_url']
            	    api_hit_count += 1
            	else: 
            		contine_API_calls = False

            print "API hit count: ", api_hit_count

        return redirect('campaign_detail', pk=campaign.pk)
    else:
        form = PostForm()

    return render(request, 'ig_miner_app/new_campaign.html', {'form': form})