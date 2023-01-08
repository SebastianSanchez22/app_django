import datetime

from django.test import TestCase
from django.urls.base import reverse
from django.utils import timezone

from .models import Question

def create_question(question_text, days):
        """create a question with the given question_text and published the given number of days offset to now
            (negative for questions published in the past, positive for questions that have not been published yet)        
        """
        time = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_questions(self):
        """was_published_recently returns False for questions whose pud_date is in the future"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text="¿Cual es el mejor CD de Platzi?", pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_present_questions(self):
        """was_published_recently() must return True for questions whose pub_date is actual"""
        time = timezone.now()
        present_question = Question(question_text="¿Quien es el mejor CD de Platzi?",pub_date=time)
        self.assertIs(present_question.was_published_recently(), True)

    def test_was_published_recently_with_past_questions(self):
        """was_published_recently() must return Flase for questions whose pub_date is more than 1 day in the past"""
        question = create_question("Future question", days=30)
        self.assertIs(question.was_published_recently(), False)

class QuestionIndexViewTest(TestCase):

    def test_no_questions(self):
        """If no question exists, an appropiate message is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_questions(self):
        """Questions with a pub_date in the future aren't displayed on the index page"""
        create_question("Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_questions(self):
        """Questions with a pub_date in the past are displayed on the index page"""
        question = create_question("Past question", days=-10)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])

    
        
        
