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
from algorithm.ob_sn import *


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
        sku_bin = self.post_data.get("sku_bin")
        second_qty = self.post_data.get("second_qty")
        min_batch = self.post_data.get("min_batch")
        try:
            libs.validator.required(co_id, 'co_id')
            libs.validator.order_for_grouping(order_src, 'order_src')
            libs.validator.dict_str(sku_bin, 'sku_bin')
            libs.validator.integer(second_qty, 'second_qty', 1, 100)
            libs.validator.integer(min_batch, 'min_batch', 1, 500)
        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return

        logging.info('ob_sn  co_id: {} second_qty: {} min_batch: {} order_qty: {} bin_qty: {}'
                     .format(co_id, second_qty, min_batch, len(order_src), len(sku_bin)))
        covered, batch_sn, second_sn = ob_sn_parallel(
            order_src, sku_bin, dict(), second_qty, min_batch, 10000)

        self.send_to_client_non_encrypt(200, message='success',
                                        response={'covered': covered, 'batch_sn': batch_sn, 'second_sn': second_sn})
