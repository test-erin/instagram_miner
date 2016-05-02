from django.shortcuts import render, get_object_or_404, redirect
from .models import Campaign, Photo
from .forms import PostForm
import os
import requests
import time

def campaign_list(request):
	campaigns = Campaign.objects.order_by('Campaign_Title')
	    
	return render(request, 'ig_miner_app/campaign_list.html', {'campaigns': campaigns})


def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)

    # Need to query the DB to find all Photos assoc. with this campaign


    return render(request, 'ig_miner_app/campaign_detail.html', {'campaign': campaign})


def new_campaign(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            campaign = form.save()

            # Make API call for campaign & store Photo data to DB. 
            ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
            hashtag = campaign.Hashtag
            pattern = '%m/%d/%Y'
            start_date = int(time.mktime(time.strptime(campaign.Start_Date, pattern)))
            end_date = int(time.mktime(time.strptime(campaign.End_Date, pattern)))
            contine_API_calls = True
            api_hit_count = 0
            url = "https://api.instagram.com/v1/tags/%s/media/recent?access_token=%s" % (hashtag, ACCESS_TOKEN)
            
            while contine_API_calls:

                response = requests.request("GET", url)
                jdict = response.json()
                data = jdict['data']

                for each in data:
                    post_date_epoch = int(each[u'created_time'])


                    if (post_date_epoch < end_date) and (post_date_epoch >= start_date) and (each[u'type'] == u'Photo'):

	                    print "#### STARTING NEW POST ####################"
	                    created_date = post_date_epoch
	                    print "created date: ", created_date
	                    print type(created_date)
	                    img_url = str(each[u'Photos'][u'low_resolution'][u'url'])
	                    print "img_url: ", img_url
	                    print type(img_url)
	                    post_link = str(each[u'link'])
	                    print "post_link: ", post_link
	                    print type(post_link)
	                    img_owner = str(each[u'user'][u'username'])
	                    print "img_owner: ", img_owner
	                    print type(img_owner)
	                    print "#### ENDING POST ####################"		
	                    print ""
	                    print ""

	                    new_Photo_record = Photo(hashtag=hashtag,
	                    	                     img_url=img_url,
	                    	                     img_owner=img_owner,
	                    	                     post_link=post_link,
	                    	                     pub_date=created_date)
	                    new_Photo_record.save()

                if jdict["pagination"]["next_url"]:
            	    url = jdict["pagination"]["next_url"]
            	    api_hit_count += 1
            	else: 
            		contine_API_calls = False

        return redirect('campaign_detail', pk=campaign.pk)
    else:
        form = PostForm()

    return render(request, 'ig_miner_app/new_campaign.html', {'form': form})