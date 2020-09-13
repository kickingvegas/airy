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




