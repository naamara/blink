import requests
import json
from remit import settings as settings
from remit import utils as utils

rest_url = settings.JUMIO_URL
token = settings.JUMIO_TOKEN
secret_key = settings.JUMIO_SECRET
success_url=settings.JUMIO_SUCCESS_URL
error_url=settings.JUMIO_ERROR_URL
user_agent=settings.JUMIO_USER_AGENT
callback_url=settings.JUMIO_CALLBACK


class Jumio:
    """
    Handle jumio data
    """

    def auth_token(self):
        """
        get and return auth token
        """
        response_data={}
        scan_ref = utils.random_string_generator(15)

        headers = {
            'accept':'application/json',
            'content-Type':'application/json',
            'user-agent':user_agent,
            'Content-Length':'0'
        }

        user_data = {
            'merchantIdScanReference':scan_ref,
            'successurl':success_url,
            'error_url':error_url,
            'callbackUrl':callback_url,
        }

        data = requests.post(
            rest_url,
            headers=headers,
            data=json.dumps(user_data),
            auth=(token,secret_key)
        )

        #
        try:
            data = requests.post(
                rest_url,
                headers=headers,
                data=json.dumps(user_data),
                auth=(token,secret_key)
            )
            print 'jumio success: ',str(data.json())
        except Exception as e:
            print 'Jumio Error: ',str(e)
        #

        response = data.json()

        response_data['scan_ref']=scan_ref
        response_data['auth_token']=response[u'authorizationToken']

        #print str(response)

        #return response[u'authorizationToken']
        return response_data
