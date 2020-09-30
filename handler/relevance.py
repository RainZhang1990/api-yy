import libs.validator
from handler.api import APIHandler
from .api import authenticated_async
from algorithm.relevance import relevance_async


class RelevanceHandler(APIHandler):

    @authenticated_async
    async def post(self):
        data = self.post_data.get("data")
        dim = self.post_data.get("dim")
        top = self.post_data.get("top")
        try:
            libs.validator.relevance(data)
            libs.validator.integer(dim, 2, 3)
            libs.validator.integer(top, 1, 500)
        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return

        result = relevance_async(data, dim, top)
        self.send_to_client_non_encrypt(
                200, message='success', response=result)
