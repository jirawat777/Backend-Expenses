from src.customer.models.queue import Queue
from src.customer.models.chat_ticket import ChatTicket
from src.users.models import User
from src.contacts.models import Contact
from src.base.response import Response
from datetime import date, datetime
import numpy
from django.db.models import Count
from src.users.model.useronpartner import UserOnPartner
from src.FCM.FCMManager import sendPush
from src.contacts.serializers import (
    ContactSearchSerializer,
)
from src.customer.serializers.chat_ticket import (
    ChatTicketSerializer,
)
from src.base.utils import (
    publicMsg
)

def updateTicket(Ticket, user_id ):
    Ticket.assignment_user_id_id = user_id
    Ticket.assignment_datetime = datetime.today()
    Ticket.status_chat = 'ASM'
    Ticket.save()
    return Ticket

def sendContactList(chat, partner_id):
    contact = Contact.objects.get(id=chat.customer_platform_id.user_uid)
    contact.status = "green"
    contact.save()
    public_data = {
        'action': 'CONTACT_LIST',
        'room': 'PARTNER:{}'.format(partner_id),
        'data': {
            'contact': ContactSearchSerializer(contact).data,
            'status_chat': ChatTicketSerializer(chat).data['status_chat']
        }
    }
    publicMsg('OPERATOR', 'CONTACT_LIST', public_data)

    public_data = {
        'action': 'CHAT_NOTIFICATION',
        'room': 'PARTNER:{}'.format(partner_id),
        'data': {
            'contact': ContactSearchSerializer(contact).data,
            'status_chat': ChatTicketSerializer(chat).data['status_chat']
        }
    }
    publicMsg('OPERATOR', 'CHAT_NOTIFICATION', public_data)
# import logging
# logging.basicConfig(filename='/var/log/fcm.log', level=logging.INFO)
def roundRobin(ticket_id, partner_id):
    chat = ChatTicket.objects.get(id=ticket_id)
    if chat.status_chat != 'NEW':
        # logging.info('no NEW status')
        return 'no NEW status'

    on_partner = UserOnPartner.objects.filter(partner_id__id=partner_id).values_list('user_id__id', flat=True)
    UserList = User.objects.all().filter(role='user', status='ONL', id__in=on_partner).exclude(status__in=['OFF','BUS','ALW'])
    if len(UserList) == 0:
        # logging.info('no User')
        return 'no User'

    chatAssign = ChatTicket.objects.exclude(assignment_user_id=None)
    chatAssign = chatAssign.filter(assignment_user_id__in=UserList,assignment_datetime__date=date.today()).exclude(status_chat__in=['NEW', 'RES'])
    user_queue_total = chatAssign.values('assignment_user_id').annotate(total=Count('assignment_user_id')).order_by('total')
    user_no_queue = UserList.exclude(id__in=user_queue_total.values_list('assignment_user_id__id', flat=True))
    if len(user_no_queue) != 0:
        # logging.info('ASM IF 1')
        chat = updateTicket(chat, user_no_queue[0])
        sendContactList(chat, partner_id)
        # logging.info('ASM IF AS 1 id = '+str(chat.assignment_user_id.id))
        # logging.info('ASM IF CT 1 id = '+str(chat.customer_platform_id.user_uid))
        sendPush(user_as_id=chat.assignment_user_id.id,tmp_dict=chat.customer_platform_id.user_uid,partner_id="ASM",msg="")
        return user_no_queue[0]

    if len(user_queue_total) != 0:
        # logging.info('ASM IF 2')
        chat = updateTicket(chat, user_queue_total[0]['assignment_user_id'])
        sendContactList(chat, partner_id)
        # logging.info('ASM IF AS 2 id = '+str(chat.assignment_user_id.id))
        # logging.info('ASM IF CT 2 id = '+str(chat.customer_platform_id.user_uid))
        sendPush(user_as_id=chat.assignment_user_id.id,tmp_dict=chat.customer_platform_id.user_uid,partner_id="ASM",msg="")
        return user_queue_total[0]['assignment_user_id']
