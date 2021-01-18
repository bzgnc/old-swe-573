from datetime import datetime, timedelta, time
import sys
from itertools import islice
from time import sleep

# from GetOldTweets3 import models
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from .praw_reddit_scraper import RedditScrapeManager
from .forms import SubredditForm

from .models import LocalTweet

User = get_user_model()


# Create your views here.

@login_required(login_url="/accounts/login/")
def homepage(request):
    return render(request, 'WebApp/home.html')


def index(request):
    subreddit_form = SubredditForm()
    return render(request, 'WebApp/home.html', {'subreddit_form': subreddit_form})


def about(request):
    return render(request, 'WebApp/about.html')


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'WebApp/home.html', {"customers": 10})


def get_data(request, *args, **kwargs):
    data = {
        "sales": 100,
        "customers": 10,
    }
    return JsonResponse(data)


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        qs_count = User.objects.all().count()
        labels = ['Users', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange']
        default_items = [qs_count, 23, 2, 3, 12, 2]
        data = {
            "labels": labels,
            "default": default_items
        }
        return Response(data)


def analyze_sentiment(request):
    subreddit = request.GET.get('subreddit')
    # Initialize instance of RedditScrapeManager, to call methods on
    scrape_instance = RedditScrapeManager(subreddit)
    # Get subreddit title, subscriber count, and description for banner
    subreddit_info = scrape_instance.get_subreddit_info()
    # Get all submission/comment info
    master_submission_data_list = scrape_instance.get_submission_data()
    # Calculate total average sentiment score from all submissions, and append to subreddit_info dictionary
    subreddit_total_sentiment_score = 0
    subreddit_total_num_comments = 0
    for submission in master_submission_data_list:
        subreddit_total_num_comments += len(submission['comments'])
        subreddit_total_sentiment_score += submission['average_sentiment_score'] * (len(submission['comments']))
    subreddit_average_sentiment_score = subreddit_total_sentiment_score / subreddit_total_num_comments
    subreddit_info['average_sentiment_score'] = round(subreddit_average_sentiment_score, 1)

    if scrape_instance.sub_exists():
        args = {'subreddit': subreddit, 'subreddit_info': subreddit_info,
                'master_submission_data_list': master_submission_data_list}
        return render(request, 'analyze_sentiment.html', args)

    '''
    Form validation logic. WIP.
    else:
        form = SubredditForm()
        return render(request, 'index.html', {'subreddit_form': form})
    '''
