from pylium.core.header import Header

class MissingImplH(Header):
    __class_type__ = Header.ClassType.Header
    # No __implementation__ attribute
    # No corresponding _impl.py or __impl__.py file will be created

    def __init__(self, val=0):
        self.val = val
        super().__init__()

    def get_val(self):
        return self.val 