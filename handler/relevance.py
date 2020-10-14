import logging
import libs.validator
from handler.api import APIHandler
from .api import authenticated_async
from algorithm.relevance import relevance_async

class RelevanceHandler(APIHandler):

    @authenticated_async
    async def post(self):
        co_id = self.post_data.get('co_id', None)
        order_src = self.post_data.get("order_src")
        dim = self.post_data.get("dim")
        top = self.post_data.get("top")
        try:
            libs.validator.required(co_id, 'co_id')
            libs.validator.order_for_relevance(order_src, 'order_src')
            libs.validator.integer(dim, 'dim', 2, 3)
            libs.validator.integer(top, 'top', 1, 500)
        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return

        logging.info('relevance  co_id: {} dim: {} top: {}'.format(co_id, dim, top))
        result = {'items': relevance_async(order_src, dim, top)}
        self.send_to_client_non_encrypt(
                200, message='success', response=result)
