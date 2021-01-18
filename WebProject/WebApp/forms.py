from django import forms

class SubredditForm(forms.Form):
    subreddit = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. politics'}), label='r/')