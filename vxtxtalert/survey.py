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
        user_id = message.user()
        content = (message['content'] or '').strip()
        # keep the audit trail
        participant = self.pm.get_participant(user_id)
        participant.add_received_message(message)
        participant.continue_session = True

        last_question = self.pm.get_last_question(participant)
        if last_question and not content:
            print '1'
            reply = self.ask_question(participant, last_question)
        elif last_question and content:
            print '2'
            error_reply = self.answer_question(participant,
                                            last_question, content)
            if error_reply:
                reply = error_reply
            else:
                next_question = self.pm.get_next_question(participant)
                reply = self.ask_question(participant, next_question)
        else:
            print '3'
            next_question = self.pm.get_next_question(participant)
            reply = self.ask_question(participant, next_question)

        print participant.dump()
        self.pm.save_participant(participant)
        continue_session = self.pm.has_more_questions_for(participant)
        self.reply_to(message, reply, continue_session=continue_session)


    def ask_question(self, participant, question):
        self.pm.set_last_question(participant, question)
        participant.has_unanswered_question = True
        return question.copy

    def answer_question(self, participant, question, answer):
        return self.pm.submit_answer(participant, answer)
