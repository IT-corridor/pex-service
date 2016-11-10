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
days = calendar.monthrange(today.year, today.month)

for token in Token.objects.all():   
    print token.owner_id, today-token.created_at, '@@@@@@'
    if token.created_at == today - timedelta(days=27):
        # send notification
        subject = 'Token Billing cycle'
        emailbody = "{}'s token is reaching the end of the billing cycle soon".format(token.owner.email)
        customfunction.sendMail('PEX+', 'jason.5001001@gmail.com', subject, emailbody, '')
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
