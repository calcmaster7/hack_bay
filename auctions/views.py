from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse
from django import forms 
from .models import User
from .models import Listing
from .models import Bid
from .models import Comment
from decimal import Decimal 
from django.contrib import messages 
from django.db.models import Count



def index(request):
    return render(request, "auctions/index.html", {
        "active_listings" : Listing.objects.all()
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

class CreateNewListingForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.DecimalField(label="Starting Bid")
    category = forms.CharField(label="Category")
    image_url = forms.CharField(label="Image URL")

class see_listing(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.DecimalField(label="Starting Bid")
    category = forms.CharField(label="Category")
    image_url = forms.CharField(label="Image URL")

#class CommentForm(forms.Form):
   # comment_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
class CommentForm(forms.Form):
    comment_text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'placeholder': 'Make comment'  # Add this
            }
        ),
        label="",
        required=True
    )

def create_listing(request):
    if request.method == 'GET':
        form = CreateNewListingForm()
        return render(request, 'auctions/clisting.html', {'form': form})
    else:
        if request.method == 'POST':
            form = CreateNewListingForm(request.POST)
        # Validate form data
        if form.is_valid():
            # Save the new listing
            new_listing = Listing(
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    min_start_bid=form.cleaned_data['starting_bid'],
                    category=form.cleaned_data['category'],
                    image_url=form.cleaned_data['image_url'],
                    listing_creator= request.user,
                    active = True
                    )
            new_listing.save()

            # Redirect to the index page (or another page of your choice)
            return HttpResponseRedirect(reverse("index"))

def listing_detail(request, listing_id):

    listing = Listing.objects.get(pk=listing_id)  

    if listing.winner is None:  # if listing.winner is NOT NONE, then the listing.winner has already been set, no need to sort the bids again
        winning_bid = listing.highest_bid() 
        if winning_bid is not None: # if winning_bid is None, that means listing.winner hasnt been set, it is currently None, and that is ok. 
            listing.winner = winning_bid.user 
            listing.save()

    if listing.winner == request.user:   # if the current user won
        context = {
            'listing': listing,
            'comment_form' : CommentForm(),
            'winner_string': "Congrats, you are the winner of this auction!"
        }
    elif listing.winner is not None:  # if we need to inform about another user winning
        context = {
            'listing': listing,
            'comment_form' : CommentForm(),
            'winner_string': f"{listing.winner.username} has won the auction!"
        }
    elif listing.winner is None and listing.active is False:
       context = {
            'listing': listing,
            'comment_form' : CommentForm(),
            'winner_string': "The auction owner decided to close the auciton before a single bid has been made!"
        } 
    else:      # if no one is currently the winner
        context = {'listing': listing,
                   'comment_form' : CommentForm()
        }
     
    return render(request, 'auctions/listing.html', context)

def update_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)  
    if request.method == 'POST':
        if request.POST.get('watchlist') == "yes":
            request.user.watchlist.add(listing)
        else:
            request.user.watchlist.remove(listing)
        return redirect('listing_detail', listing_id=listing.id)

def place_bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.method == 'POST' and request.user.is_authenticated:
        bid_amount = Decimal(request.POST['bid_amount'])

        # We get the highest bid using the highest_bid() method. If no bids have been made yet, 
        # it will return None, and we'll consider the minimum start bid as the highest bid.
        highest_bid = listing.highest_bid()
        if highest_bid is not None:
            highest_bid_amount = highest_bid.bid_ammount
        else:
            highest_bid_amount = listing.min_start_bid

        # We check if the bid is valid (i.e., greater than the current highest bid and the listing is active).
        if bid_amount > highest_bid_amount and listing.active:
            # Instead of updating a field in the Listing model, we now create a new Bid object.
            bid = Bid(listing=listing, bid_ammount=bid_amount, user=request.user)
            bid.save()
            messages.success(request, "Congrats! You are currently the highest bidder!")
        else:
            messages.error(request, 'Your bid must be higher than the current highest bid and the minimum bid.')
        return redirect('listing_detail', listing_id=listing.id)

def make_comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)

        if form.is_valid():
            comment_text = form.cleaned_data.get('comment_text')

            if comment_text.strip() == '':
                messages.error(request, 'You cannot submit an empty comment.')
            else:
                comment = Comment(listing=listing, text=comment_text.strip(), user=request.user)
                comment.save()
        else:
            # This else branch is for cases where the form is not valid
            messages.error(request, 'There was an error with your comment submission.')
        
    return redirect('listing_detail', listing_id=listing.id)

def close_auction(request,listing_id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=listing_id)
        if request.user == listing.listing_creator:  # Check if the user is the creator of the listing
            listing.active = False  # Set the listing as inactive
            listing.save()  # Save the changes
            messages.success(request, "You have now closed the auction!")
        else:
            messages.error(request, "Only the auction creator can close the auction.")
        return redirect('listing_detail', listing_id=listing.id) 

def watchlist(request):
    if request.user.is_authenticated:
        watchlist_items = request.user.watchlist.all()
        context = {'watchlist_items': watchlist_items}
        return render(request, 'auctions/watchlist.html', context)
    else:
        return redirect('login')  # redirect to login page if user is not authenticated

def categories(request):
    categories = Listing.objects.values('category').annotate(total=Count('category')).order_by('category')
    context = {'categories': categories}
    return render(request, 'auctions/categories.html', context)

def category_listings(request, category_name):
    listings = Listing.objects.filter(category=category_name, active=True)
    context = {'listings': listings, 'category_name': category_name}
    return render(request, 'auctions/category_listings.html', context)
