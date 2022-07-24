# Utility import
import json
import uuid
import pymongo
from datetime import date, datetime
import sys
# Model import
from django.utils import timezone
from src.customer.models.chat_ticket import ChatTicket
from src.customer.models.customer_platform import CustomerPlatform
from src.customer.models.customer import Customer
from src.users.models import User
from src.contacts.models import Contact
from src.base.queue.round_robin import roundRobin
from src.webhook.functions.resolverequeue import resolverequeue
import os


import logging
import pymongo
from src.logging.logging import Logging
log = Logging("mongolog")
from src.contacts.serializers import (
    ContactSearchSerializer,
)

from src.customer.serializers.chat_ticket import (
    ChatTicketSerializer,
)

# Common import
from src.base.utils import (
    publicMsg
)
from src.base.queue.common import getQueue

# Config import
from src.config.common import MONGODBHOST, MONGO_COLLECTION

def mongo_conn():
    try:
        conn = pymongo.MongoClient(MONGODBHOST)
        print('MongoDB connected: ', conn)
        return conn
    except Exception as e:
        print('Error in mongo connection: ', e)


dbConnection = mongo_conn()
db = dbConnection.chat
messagesCol = db[MONGO_COLLECTION]
# log = Logging("mongolog")
def createChatTicket(inserted_id, user_id, latest_message, partner_id):
    contact = Contact.objects.get(platform_user_id=user_id)
    # Update Contact
    contact.latest_message_time = datetime.today()
    contact.latest_message = latest_message
    contact.latest_message_by = 'user'
    contact.save()

    # Check / Create Customer Platform and Customer
    try:
        customer_platform = CustomerPlatform.objects.get(user_uid=contact.id)
        customer = customer_platform.customer_id
    except CustomerPlatform.DoesNotExist:
        customer = Customer(
            partner_id_id=contact.partner_id,
            name=contact.displayName,
            avatar_url=contact.pictureUrl,
            create_by='-'
        )
        customer.save()
        customer_platform = CustomerPlatform(
            customer_id=customer,
            user_uid=contact.id,
            platform='LC',
            account_name=contact.displayName
        )
        customer_platform.save()

    # Check / Create ChatTicket
    try:
        chat = ChatTicket.objects.get(customer_platform_id=customer_platform, new_datetime__date=date.today())
        if chat.status_chat == 'RES':
            resolverequeue(ticket_id = chat.id,contact_id=contact)

    except ChatTicket.DoesNotExist:
        if ChatTicket.objects.filter(customer_platform_id=customer_platform, status_chat__in=['NEW','ASM'], new_datetime__date=date.today()).count() == 0:
            chat = ChatTicket(
                customer_id=customer,
                customer_platform_id=customer_platform,
                ticket_type_id=None,
                status_chat='NEW',
                new_datetime=timezone.now()
            )
            chat.save()
            contact.status = "grey"
            contact.update_status_time = timezone.now()
            contact.save()
            tmp_info = {}
            tmp_info['id chatticket'] = str(chat)
            tmp_info['new_datetime chatticket'] = str(chat.new_datetime)
            tmp_info['id customer'] = str(customer.id)
            tmp_info['id contact'] = str(contact.id)
            tmp_info['name contact'] = str(contact.displayName)
            tmp_info['name customer'] = str(customer.name)
            tmp_info['status chat'] = str(chat.status_chat)
             
            log.info(action = "Create Chatticket", line = "create 90",date=timezone.now(), data=tmp_info)
            queue = getQueue(uuid.UUID(partner_id).int)
            queue.enqueue(roundRobin, chat.id, partner_id)

    # Public CHAT_MESSAGE
    public_data = {
        'action': 'CHAT_MESSAGE',
        'room': 'CONTACT:{}'.format(contact.id),
        'data': {
            'message': json.loads(json.dumps(list(messagesCol.find({'_id': inserted_id}))[0], default=lambda o: str(o))),
        }
    }
    publicMsg('OPERATOR', 'CHAT_MESSAGE', public_data)

    # Public CONTACT_LIST
    public_data = {
        'action': 'CONTACT_LIST',
        'room': 'PARTNER:{}'.format(partner_id),
        'data': {
            'contact': ContactSearchSerializer(contact).data,
            'status_chat': ChatTicketSerializer(chat).data['status_chat']
        }
    }
    publicMsg('OPERATOR', 'CONTACT_LIST', public_data)

    # Public CHAT_NOTIFICATION
    public_data = {
        'action': 'CHAT_NOTIFICATION',
        'room': 'PARTNER:{}'.format(partner_id),
        'data': {
            'contact': ContactSearchSerializer(contact).data,
            'status_chat': ChatTicketSerializer(chat).data['status_chat']
        }
    }
    publicMsg('OPERATOR', 'CHAT_NOTIFICATION', public_data)
