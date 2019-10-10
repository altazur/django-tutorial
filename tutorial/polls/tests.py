import datetime
from django.test import TestCase
from .models import Question
from django.utils import timezone
from django.urls import reverse


# Create your tests here.

def create_question(question_text, days, choice=1):
    """
    Create a question with given text and days pasted from now.
    Negative days means that question is in the past from now
    and positive days is that the question is in the future.
    0 means now
    If the choice is not 0 (default) than the created question will have a on test choice
    In other way the question won't have any choice and therefore won't be displayed on any pages
    """
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    if choice==0:
        return question
    elif choice != 0:
        question.choice_set.create(choice_text="test",votes=0)
        return question
    return question

class QuestionIndevViewTests(TestCase):
    def test_no_question(self):
        """
        Check the correct response and text if there is no questions
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question(self):
        """ Check that no future questions are not displayed on the page"""
        create_question("Future question", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """Check that past question are displayed on the page"""
        create_question("Past question", -1)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question>'])

    def test_today_question(self):
        """Check that today question are displayed on the page"""
        create_question("Today", 0)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Today>'])

    def test_two_past_question(self):
        """Check that two past question are displayed both"""
        create_question("Past 1", -30)
        create_question("Past 2", -15)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past 2>', '<Question: Past 1>'])

    def test_past_and_future_question(self):
        """Check that with two question only past ones are shown"""
        create_question("Past", -30)
        create_question("Future", 30)
        response = self.client.get(reverse('polls:index'))
        self.assertTrue(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past>'])

class QuestionDetailViewTests(TestCase):
    def test_past_question(self):
        """Past question is visible by its url"""
        question = create_question("Past", -30)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_future_question(self):
        """Future question isn't visible by url"""
        question = create_question("Future", 30)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class QuestionResultsViewTests(TestCase):
    def test_past_question(self):
        """Future question result page isn't available by url"""
        past_question = create_question("Past", -30)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_future_question(self):
        """Future question result page isn't available by url"""
        future_question = create_question("Future", 30)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class QuestionWithoutChoiceTests(TestCase):
    def test_question_without_choice(self):
        """Question without choice isn't displayed on the index page and can't be accessed by url on result and details pages"""
        question_without_choice = create_question("Without choice", -30, 0)
        response = self.client.get(reverse('polls:index'))
        self.assertNotContains(response,"Without choice")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
        detail_url = reverse('polls:detail', args=(question_without_choice.id,))
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)
        result_url = reverse('polls:results', args=(question_without_choice.id,))
        response = self.client.get(result_url)
        self.assertEqual(response.status_code, 404)

    def test_question_with_choice(self):
        """Question with choice is displayed on the index page and can by accessed by url everywhere"""
        question_with_choice = create_question("With choice", -30)
        #question_with_choice.choice_set.create(choice_text="test", votes=0) 
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response,"With choice")
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: With choice>'])
        detail_url = reverse('polls:detail', args=(question_with_choice.id,))
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        result_url = reverse('polls:results', args=(question_with_choice.id,))
        response = self.client.get(result_url)
        self.assertEqual(response.status_code, 200)

class QustionModelTests(TestCase):
    def test_was_added_recently_with_future_question(self):
        """
        was_added_recently() returns False if the qustion.pub_date is in the future
        """
        time = timezone.now()+datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_added_recently(), False)

    def test_was_adeed_recently_with_old_question(self):
        """
        was_added_recently() returns False if the question is older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        past_question = Question(pub_date=time)
        self.assertIs(past_question.was_added_recently(), False)

    def test_was_added_recently_with_recent_question(self):
        """
        was_added_recently() return True if the question was added within 1 last 24 hours
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        question_within_one_day = Question(pub_date=time)
        self.assertIs(question_within_one_day.was_added_recently(), True)
