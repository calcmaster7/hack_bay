from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watching_users")
    
    def __str__(self):
        watchlist_items = ", ".join(str(listing.id) for listing in self.watchlist.all())
        return f"Username: {self.username}, watchlist: [{watchlist_items}]"

class Listing(models.Model):
    title = models.CharField(max_length=128)
    category = models.CharField(max_length=64)
    image_url = models.URLField(max_length=200, blank=True)
    description = models.TextField()
    min_start_bid = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    active = models.BooleanField()
    listing_creator = models.ForeignKey(User,on_delete=models.CASCADE,related_name="created_listings")
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='won_listings')

    def highest_bid(self):
        return self.bids.order_by('-bid_ammount').first()

    def __str__(self):
        highest_bid = self.highest_bid()
        highest_bid_str = str(highest_bid.bid_ammount) if highest_bid else "None"
        return f"{self.title},{self.category},{self.image_url},{self.description},{self.min_start_bid},{self.active},{self.listing_creator}, highest bid: {highest_bid_str}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bid_ammount = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    timestamp = models.DateTimeField(auto_now_add=True)

 
    def __str__(self):
        return f"{self.listing},{self.bid_ammount},{self.user},{self.timestamp}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    text = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.listing},{self.user},{self.timestamp} {self.text}"
