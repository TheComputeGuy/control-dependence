class CdgStackEntry:
    # Does not implement calling context for recursive calls
    def __init__(self, address, instance, ipd):
        self.address: str = address
        self.instance: int = instance
        self.ipd: str = ipd