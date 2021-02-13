class AssetPrettyPrinter(dict):
    """ Print assets in nice two columns """

    def __str__(self) -> str:
        format_item = lambda k, v: "{: <20}: {}".format(k, v)
        items = [format_item(k, v) for k, v in self.items() if v != 0]
        return "\n".join(items)
