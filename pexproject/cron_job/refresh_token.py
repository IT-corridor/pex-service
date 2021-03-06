import os
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pexproject.settings")

from pexproject.models import Token
import datetime
import calendar
from datetime import timedelta 
from pexproject.scrapers import customfunction


today = datetime.datetime.now().date()
days = calendar.monthrange(today.year, today.month)[1]

for token in Token.objects.all():   
    if token.created_at == today - timedelta(days=days-5):
        # send notification
        subject = 'Token Billing cycle'
        emailbody = "{}'s token is about to reach to the end of the billing cycle. His search count will reset in 5 days. Please update the customer and make sure the customer has paid for the upcoming billing cycle.".format(token.owner.email)

        resp = customfunction.sendMail('PEX+', 'info@pexportal.com', subject, emailbody)
        if resp != "sent":
            print 'Something is wrong!'
    elif token.created_at == today - timedelta(days=days):
        # save history
        log_item = "{} ~ {}#{}#{}@".format(str(token.created_at), str(today), token.limit_flight_search, token.run_flight_search)
        token.refresh_log = log_item + token.refresh_log

        # update date
        token.created_at = today
        token.number_update = token.number_update + 1 

        # check carryover
        if token.carry_over:
            token.limit_flight_search = token.limit_standard + (token.limit_flight_search - token.run_flight_search)
            token.limit_qpx = token.limit_standard + (token.limit_qpx - token.run_flight_search)
        else:
            token.limit_flight_search = token.limit_standard
            token.limit_qpx = token.limit_standard

        # clear counters
        token.run_flight_search = 0
        token.run_hotel_search = 0

        # save token
        token.save()
