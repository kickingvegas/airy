##
# Copyright 2020 Charles Y. Choi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from twilio.rest import Client

class SMSMessenger:
    def __init__(self, account_sid, auth_token, fromNumber):
        self.fromNumber = fromNumber
        self.client = Client(account_sid, auth_token)

    def sendMessage(self, to, body):
        message = self.client.messages.create(body=body,
                                              from_=self.fromNumber,
                                              to=to)

        print(message.sid)




