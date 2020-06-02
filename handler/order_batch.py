import json
import time
import datetime

import libs.validator
from handler.api import APIHandler
from core.config import Config
from .api import authenticated_async
from libs import zbase62
import algorithm.ob


class OrderBatchLPHandler(APIHandler):
    ''' get order batch through the lp method.
    '''

    @authenticated_async
    async def post(self):
        try:
            libs.validator.orderForGrouping(
                self.post_data.get("orderDetail"))
            libs.validator.batch(self.post_data.get("batch"))

        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(-1, message=e.__str__())
            return

        orderDetail = self.post_data.get("orderDetail")
        batch = self.post_data.get("batch")

        result = algorithm.ob.ob_lp(orderDetail, batch)

        if not result['lpstatus'] == 'Optimal':
            self.send_to_client_non_encrypt(202, message='failure',
                                            response={'status': result['status'], 'value': -1, 'items': []})
            return
        else:
            self.send_to_client_non_encrypt(
                200, message='success', response=result)
