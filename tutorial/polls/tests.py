import datetime
from django.test import TestCase
from .models import Question
from django.utils import timezone

# Create your tests here.

class QustionModelTests(TestCase):
    
    def test_was_added_recently_with_future_question(self):
        """
        was_added_recently() returns False if the qustion.pub_date is in the future
        """
        time = timezone.now()+datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_added_recently(), False)
