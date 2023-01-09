import datetime

from django.test import TestCase
from django.urls.base import reverse
from django.utils import timezone

from .models import Question, Choice

def create_question(question_text, days):
        """create a question with the given question_text and published the given number of days offset to now
            (negative for questions published in the past, positive for questions that have not been published yet)        
        """
        time = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(choice_text, votes, question_id):
        """create a choice with the given choice_text, number of votes and corresponding question""" 
        return Choice.objects.create(choice_text=choice_text, votes=votes, question_id=question_id)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_questions(self):
        """was_published_recently must return False for questions whose pub_date is in the future"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = create_question("Future question", days=30)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_present_questions(self):
        """was_published_recently() must return True for questions whose pub_date is actual"""
        present_question = create_question("Present question", days=0)
        self.assertIs(present_question.was_published_recently(), True)

    def test_was_published_recently_with_past_questions(self):
        """was_published_recently() must return False for questions whose pub_date is more than 1 day in the past"""
        past_question = create_question("Past question", days=-30)
        self.assertIs(past_question.was_published_recently(), False)

class QuestionIndexViewTest(TestCase):

    def test_no_questions(self):
        """If no question exists, an appropiate message is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(
            response.context["latest_question_list"], []
            )

    def test_future_questions(self):
        """Questions with a pub_date in the future aren't displayed on the index page"""
        create_question("Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context["latest_question_list"], []
            )

    def test_past_questions(self):
        """Questions with a pub_date in the past are displayed on the index page"""
        question = create_question("Past question", days=-10)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"], [question]
            )

    def test_future_question_and_past_question(self):
        """Even if both past and future questions exists, only past questions are displayed"""
        past_question = create_question(question_text="Past question", days=-30)
        future_question = create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"], [past_question]
            )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions"""
        past_question1 = create_question(question_text="Past question 1", days=-30)
        past_question2 = create_question(question_text="Past question 2", days=-40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"], [past_question1, past_question2]
            )

    def test_two_future_questions(self):
        """Future questions may not display even if there are many"""
        future_question1 = create_question(question_text="Future question 1", days=30)
        future_question2 = create_question(question_text="Future question 2", days=40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"], []
            )

class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """The detail view of a question with a pub_date in the future returns a 404 error not found"""
        future_question = create_question(question_text="Future question", days=30)
        url = reverse("polls:detail", args=(future_question.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """The detail view of a question with a pub_date in the past displays the question's text"""
        past_question = create_question(question_text="Past question", days=-30)
        url = reverse("polls:detail", args=(past_question.pk,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class ChoiceResultsViewTests(TestCase):

    def test_only_one_vote(self):
        """If the number of votes choice of a specific question is 1, display question text -- 1 vote"""
        question = create_question(question_text="Test Question", days=-10)
        choice = create_choice(choice_text="Choice text", votes=1, question_id=question.pk)
        url = reverse("polls:results", args=(choice.pk,))
        response = self.client.get(url)
        self.assertNotContains(
            response, f'{choice.choice_text} &nbsp; | &nbsp; {choice.votes} votes'
            )
        self.assertContains(
            response, f'{choice.choice_text} &nbsp; | &nbsp; {choice.votes} vote'
            )

    def test_many_votes(self):
        """If the number of votes choice of a specific question is n, display question text -- n votes"""
        question = create_question(question_text="Test Question", days=-10)
        choice = create_choice(choice_text="Choice text", votes=5, question_id=question.pk)
        url = reverse("polls:results", args=(choice.pk,))
        response = self.client.get(url)
        self.assertContains(
            response, f'{choice.choice_text} &nbsp; | &nbsp; {choice.votes} votes'
            )
        