from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.listing_detail, name="listing_detail"),
    path('listing/<int:listing_id>/update_watchlist', views.update_watchlist, name='update_watchlist'),
    path('listing/<int:listing_id>/place_bid', views.place_bid, name='place_bid'),
    path('listing/<int:listing_id>/close_auction', views.close_auction, name = 'close_auction'),
    path('listing/<int:listing_id>/make_comment', views.make_comment, name = 'make_comment'),
    path('watchlist',views.watchlist,name='watchlist'),
    path('categories', views.categories, name='categories'),
    path('categories/<str:category_name>', views.category_listings, name='category_listings')
    
]
