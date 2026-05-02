from django.urls import path
from . import views


urlpatterns = [
path('', views.home, name='home'),
path('projects/', views.projects_list, name='projects_list'),
path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
path('schools/', views.schools_list, name='schools_list'),
path('schools/<int:pk>/', views.school_detail, name='school_detail'),
path('schools/<int:pk>/students/', views.load_students, name='load_students'),
path('schools/<int:pk>/teachers/', views.load_teachers, name='load_teachers'),
path('schools/<int:pk>/achievements/', views.load_achievements, name='load_achievements'),
path('gallery/', views.gallery, name='gallery'),
path ('newsletter_signup/', views.newsletter_signup, name= 'newsletter_signup'),
path('donate/', views.donate, name='donate'),
path('sermons/', views.sermons, name='sermons'),
path("verify-payment/", views.verify_payment, name="verify_payment"),
path('contact/', views.contact, name='contact'),
path('ministries/men/', views.men_ministry, name='men_ministry'),
path('ministries/women/',views.women_ministry, name='women_ministry'),
path('ministries/youth/',views.youth_ministry, name='youth_ministry'),
path('ministries/children/',views.children_ministry, name='children_ministry'),
 # PRAYER REQUEST (AJAX)
path("prayer-request/", views.prayer_request, name="prayer_request"),

    # EVENTS
path("events/", views.events_list, name="events_list"),
path("events/<slug:slug>/", views.event_detail, name="event_detail"),

    # PASTORAL TEAM
path("pastoral-team/", views.pastoral_team, name="pastoral_team"),

]