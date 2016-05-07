from django.db import models
from django.utils import timezone

# Django automatically adds an autoincrementing primary key to each table
# Date provided by user in new_campaign view converted to epoch time before DB storage
# Column names capitalized for purposes of Django admin pages & form labels

# Need to add users table so each user can have multiple campaigns.
# Need to add ForeignKey btwn Campaign & Photo. Much difficulty w/ Django's built-in ORM


class Campaign(models.Model):
    Campaign_Title = models.CharField(max_length=100, null=False,)
    Start_Date = models.CharField(max_length=10, null=False, help_text="MM/DD/YYYY")
    End_Date = models.CharField(max_length=10, null=False, help_text="MM/DD/YYYY")
    Hashtag = models.CharField(max_length=100, null=False, help_text="Don't type the '#'")

    def __str__(self):
	    """Provide helpful Campaign object representation when printed."""

	    return "%s - #%s" % (self.Campaign_Title, self.Hashtag)


class Photo(models.Model):
    hashtag = models.CharField(max_length=100, null=False)
    img_url = models.TextField(null=False)
    img_owner = models.CharField(max_length=50, null=False)
    post_link = models.TextField(max_length=300, null=False, default="http://www.google.com")
    pub_date = models.IntegerField(null=False)
    campaign_number = models.IntegerField()    # Same as pkey for each campaign

    def __str__(self):
	    """Provide helpful Photo object representation when printed."""

	    return "%s - #%s" % (self.img_owner, self.hashtag)