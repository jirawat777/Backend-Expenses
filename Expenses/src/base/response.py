from rest_framework.response import Response as _Response
from rest_framework import status as _status

def Response(data, status=None, template_name=None, headers=None, content_type=None,message=None):

    _data = {
        'data': data
    }
    if status is not None:
        _data['status'] = status
    else:
        _data['status'] = _status.HTTP_200_OK

    # handel message
    if message is not None :
        if 'code' in message and 'msg' in message:
            _data['code'] = message['code']
            _data['msg'] = message['msg']
        else:
            _data['msg'] = message
        
    return _Response(_data, status,template_name,headers,content_type)