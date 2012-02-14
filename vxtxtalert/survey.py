# -*- test-case-name: vxtxtalert.tests.test_survey -*-
# -*- coding: utf8 -*-
from twisted.internet.defer import inlineCallbacks

from vumi.application.base import ApplicationWorker


class SurveyApplication(ApplicationWorker):

    def setup_application(self):
        pass

    def teardown_application(self):
        pass

    def consume_user_message(self, message):
        pass

