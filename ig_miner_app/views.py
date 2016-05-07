from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Campaign, Photo
from .forms import PostForm
from django import forms
import os
import requests
import time
import simplejson

def campaign_list(request):
	campaigns = Campaign.objects.order_by('Campaign_Title')
	    
	return render(request, 'ig_miner_app/campaign_list.html', {'campaigns': campaigns})


def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)

    # Need to query the DB to find all Photos assoc. with this campaign
    results = Photo.objects.filter(campaign_number=pk)
    print results

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
    
    # Allow user to create a new campaign using a form

    if request.method == "POST":
        form = PostForm(request.POST)

        # Line 38 is supposed to force a user to provide an end date, but is giving me problems
        # form.clean('This field is required.')
        if form.is_valid():
            campaign = form.save()

            # Make API call for newly created campaign

            ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
            print "Access token: ", ACCESS_TOKEN
            campaign_title=campaign.Campaign_Title
            print "Campaign Title: ", campaign_title
            hashtag = campaign.Hashtag
            print "Hashtag: ", hashtag
            pattern = '%m/%d/%Y'
            start_date = int(time.mktime(time.strptime(campaign.Start_Date, pattern)))
            print "Start date: ", start_date
            end_date = int(time.mktime(time.strptime(campaign.End_Date, pattern)))
            print "end date: ", end_date
            contine_API_calls = True
            api_hit_count = 0
            print "API hit count: ", api_hit_count
            url = "https://api.instagram.com/v1/tags/%s/media/recent?access_token=%s" % (hashtag, ACCESS_TOKEN)
            
            while contine_API_calls:

            	print "In while loop #######"

                r = requests.get(url)
                print r
                jdict = r.json()
                data = jdict['data']
                pagination = jdict['pagination']

                # For each published post, if it falls within 
                # the start and end dates, add it to the database

                for each in data:
                    post_date_epoch = int(each['created_time'])

                    if (post_date_epoch < end_date) and (post_date_epoch >= start_date) and (each['type'] == 'image' or 'Image'):

	                    print "#### STARTING NEW POST ####################"
	                    created_date = post_date_epoch
	                    print "created date: ", created_date
	                    print type(created_date)
	                    img_url = str(each['images']['low_resolution']['url'])
	                    print "img_url: ", img_url
	                    print type(img_url)
	                    post_link = str(each['link'])
	                    print "post_link: ", post_link
	                    print type(post_link)
	                    img_owner = str(each['user']['username'])
	                    print "img_owner: ", img_owner
	                    print type(img_owner)
	                    print "#### ENDING POST ####################"		
	                    print ""
	                    print ""

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