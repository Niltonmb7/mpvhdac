from django.shortcuts import render
# Client SOAP
from suds.client import Client
# Per send to email
from django.core.mail import send_mail
from django.conf import settings

from urllib.request import urlopen
import requests

def reniec(username):
    # url = 'http://wsvmin.minsa.gob.pe/demowsreniecmq/serviciomq.asmx?wsdl'
    # user = '05353734'
    # passwd = 'demo123'
    # app = 'DEMORENIEC'
    # client = Client(url)
    # cli = Client(url=url, headers={'usuario': user, 'clave': passwd})
    # print(client)
    print(username)

def sendMail(mail, subject, message):
    mail_from = settings.EMAIL_HOST_USER
    recipient_list = [mail]
    send_mail(subject, message, mail_from, recipient_list)
    return True

def sendMsg(number, message):
    # https://api.labsmobile.com/get/send.php?username=jvalenzuela@hrdac-cerrodepasco.gob.pe&password=wk79tc25&message=helloworld&msisdn=051-962357499&sender=51962357499
    # https://api.labsmobile.com/get/send.php?username=jvalenzuela@hrdac-cerrodepasco.gob.pe&password=wk79tc25&message=helloworld&msisdn=51962357499&sender=SENDER
    api_url = 'https://api.labsmobile.com/get/send.php?'
    credentials = 'username=' + settings.MSG_HOST_USER + '&password=' + settings.MSG_HOST_PASSWORD
    content_msg = '&sender=SENDER&message=' + message
    url_send = api_url + credentials + "&msisdn=51" + number + content_msg
    print(url_send)
    r = requests.get(url_send)
    return True