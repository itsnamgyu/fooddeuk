import logging
from stripe.error import *


class DtStripeError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    @staticmethod
    def from_stripe_error(e: StripeError):
        logging.info("Stripe error: {}".format(e._message))
        if isinstance(e, CardError):
            return DtStripeError(code="CARD_ERROR", message=e._message)
        else:
            return DtStripeError(
                code="UNKNOWN_ERROR",
                message="There was an issue processing your request. Please try again or contact support.",
            )
