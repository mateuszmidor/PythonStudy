class InvalidTradeError(Exception):
    """ Type of trade unrecognized. Known trades: fund, withdraw, buy, sell exchange """


class CorruptedReportError(Exception):
    """ Report CSV blank empty, missing header, header malformed """


class InvalidReportRowError(Exception):
    """ Commission is not money """