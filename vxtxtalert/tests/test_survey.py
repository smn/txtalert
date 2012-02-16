from twisted.internet.defer import inlineCallbacks

from vumi.application.tests.test_base import ApplicationTestCase

from vxtxtalert.survey import SurveyApplication


class SurveyTestCase(ApplicationTestCase):

    application_class = SurveyApplication
    timeout = 1
    default_questions = [{
        'copy': 'What is your favorite colour?',
        'valid_responses': ['red', 'green', 'blue'],
    },
    {
        'copy': 'Orange, Yellow or Black?',
        'valid_responses': ['orange', 'yellow', 'black'],
    },
    {
        'copy': 'What is your favorite fruit?',
        'valid_responses': ['apple', 'orange'],
    }]

    @inlineCallbacks
    def setUp(self):
        yield super(SurveyTestCase, self).setUp()
        self.config = {
            'questions': self.default_questions,
            'transport_name': self.transport_name,
        }
        self.app = yield self.get_application(self.config)
        self.pm = self.app.pm

    def assertResponse(self, response, content):
        self.assertEqual(response['content'], content)

    def assertEvent(self, response, event):
        self.assertEqual(response['session_event'], event)

    @inlineCallbacks
    def test_initial_connect(self):
        msg = self.mkmsg_in(content=None)
        yield self.dispatch(msg)
        [response] = self.get_dispatched_messages()
        # make sure we get the first question as a response
        self.assertResponse(response, self.default_questions[0]['copy'])
        # the session event should be none so it is expecting
        # a response
        self.assertEvent(response, None)
        # get the participant and check the state after the first interaction
        participant = self.pm.get_participant(msg.user())
        next_question = self.app.pm.get_next_question(participant)
        self.assertEqual(next_question.copy, self.default_questions[1]['copy'])

    @inlineCallbacks
    def test_continuation_of_session(self):
        # create the inbound message
        msg = self.mkmsg_in(content='red')
        # prime the participant
        participant = self.pm.get_participant(msg.user())
        participant.has_unanswered_question = True
        participant.last_question_index = 0
        self.pm.save_participant(participant)
        # send to the app
        yield self.dispatch(msg)
        [response] = self.get_dispatched_messages()
        # check we get the next question and that its not a session close event
        self.assertResponse(response, self.default_questions[1]['copy'])
        self.assertEvent(response, None)
