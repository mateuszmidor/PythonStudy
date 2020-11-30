from money import Money

class Currency(object):
    """ Currency is value object with restrictions on format """

    def __init__(self, currency : str):
        valid_format_or_exception(currency)
        self.value = currency

    def __eq__(self, other) -> bool:
        return (type(other) is type(self)) and (self.value == other.value)

    def _neq__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return self.value.__hash__()

    def __str__(self) -> str:
        return self.value

def valid_format_or_exception(currency : str):
    Money("0", currency) # exception on invalid format


# predefined currencies
USD = Currency("USD")
EUR = Currency("EUR")