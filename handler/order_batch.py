import json
import time
import datetime
import logging

import libs.validator
from handler.api import APIHandler
from core.config import Config
from .api import authenticated_async
from libs import zbase62
import algorithm.ob_an
from algorithm.ob_sn import Sn


class OrderBatchAnHandler(APIHandler):

    @authenticated_async
    async def post(self):
        co_id = self.post_data.get('co_id', None)
        order_src = self.post_data.get("order_src")
        batch = self.post_data.get("batch")
        try:
            libs.validator.required(co_id, 'co_id')
            libs.validator.order_for_grouping(order_src, 'order_src')
            libs.validator.integer(batch, 'batch', 1, 9999)
        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return

        logging.info('ob_an  co_id: {} batch: {}'.format(co_id, batch))
        result = algorithm.ob_an.ob_an(order_src, batch)

        if not result['lpstatus'] == 'Optimal':
            self.send_to_client_non_encrypt(200, message='failure',
                                            response={'status': result['status'], 'value': -1, 'items': []})
            return
        else:
            self.send_to_client_non_encrypt(
                200, message='success', response=result)

class OrderBatchSnHandler(APIHandler):

    @authenticated_async
    async def post(self):
        co_id = self.post_data.get('co_id', None)
        order_src = self.post_data.get("order_src")
        second_n = self.post_data.get("second_n")
        min_batch = self.post_data.get("min_batch")
        max_batch = self.post_data.get("max_batch")
        heap_qty = self.post_data.get("heap_qty")
        try:
            libs.validator.required(co_id, 'co_id')
            libs.validator.order_for_grouping(order_src, 'order_src')
            libs.validator.integer(second_n, 'second_n', 1, 100)
            libs.validator.integer(min_batch, 'min_batch', 1, 200)
            libs.validator.integer(max_batch, 'max_batch', min_batch, 200)
            libs.validator.integer(heap_qty, 'heap_qty', 5, 500)
        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return

        logging.info('ob_sn  co_id: {} second_n: {} min_batch: {} max_batch: {} heap_qty: {}'
            .format(co_id, second_n,min_batch, max_batch, heap_qty))
        sn=Sn(order_src, second_n, min_batch, max_batch, heap_qty)
        batch_sn, second_sn = sn.fit()
        
        self.send_to_client_non_encrypt(200, message='success',
                                        response={'batch_sn': batch_sn, 'second_sn': second_sn})
