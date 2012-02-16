# -*- test-case-name: vxtxtalert.tests.test_survey -*-
# -*- coding: utf8 -*-
import hashlib
import json
from twisted.internet.defer import inlineCallbacks

from vumi.tests.utils import FakeRedis
from vumi.application.base import ApplicationWorker

from vxpolls.manager import PollManager


class SurveyApplication(ApplicationWorker):

    batch_completed_response = 'You have completed the first 5 questions, '\
                                'dial in again to complete the survey.'
    survey_completed_response = 'You have completed the survey'

    def validate_config(self):
        self.questions = self.config.get('questions', [])
        self.r_config = self.config.get('redis_config', {})
        self.batch_size = self.config.get('batch_size', 5)
        self.poll_id = self.config.get('poll_id', self.generate_unique_id())

    def generate_unique_id(self):
        return hashlib.md5(json.dumps(self.config)).hexdigest()

    def setup_application(self):
        self.r_server = FakeRedis(**self.r_config)
        self.pm = PollManager(self.r_server, self.questions,
                                    batch_size=self.batch_size)

    def teardown_application(self):
        self.pm.stop()

    def consume_user_message(self, message):
        content = message['content']
        participant = self.pm.get_participant(message.user())
        if participant.has_unanswered_question and content:
            self.on_message(participant, message)
        elif participant.has_unanswered_question and not content:
            self.resume_session(participant, message)
        else:
            self.init_session(participant, message)

    def on_message(self, participant, message):
        # receive a message as part of a live session
        last_question = self.pm.get_last_question(participant)
        error_message = self.pm.submit_answer(participant, message['content'])
        if error_message:
            self.reply_to(message, error_message)
        else:
            next_question = self.pm.get_next_question(participant)
            self.reply_to(message, next_question.copy)
            self.pm.set_last_question(participant, next_question)
            self.pm.save_participant(participant)

    def init_session(self, participant, message):
        # brand new session
        first_question = self.pm.get_next_question(participant)
        self.reply_to(message, first_question.copy)
        participant.has_unanswered_question = True
        self.pm.set_last_question(participant, first_question)
        self.pm.save_participant(participant)

    def resume_session(self, participant, message):
        # restart of an aborted session
        pass

