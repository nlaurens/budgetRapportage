class OrderList:
    orders = []  # List of orders

    def __init__(self, orders=None):
        if orders is None:
            orders = []
        self.orders = orders


    """
    Returns a dictionary of OrderList sorted out by a specific
    attributes in the order.
    For example:
        split(self, ['ordernummer', 'budgethouder'])
    will return:
        dict['order1']['budgethouder1'] = OrderList
        dict['order1']['budgethouder..'] = OrderList
        dict['order2']['budgethouder1'] = OrderList
        dict['order2']['kostensoort..'] = OrderList
        dict['order..']['kostensoort..'] = OrderList
    """
    def split(self, attributes_to_group):
        orderListDict = self.__split(attributes_to_group.pop(0))

        if attributes_to_group:
            for key, orderListDictChild in orderListDict.iteritems():
                orderListDict[key] = orderListDictChild.split(
                    list(attributes_to_group))  # list(..) creates a copy for recursion!

        return orderListDict

    def __split(self, attribute_to_group):
        orderDict = {}
        # Sort out orders for each attribute to group
        for order in self.orders:
            order_key = getattr(order, attribute_to_group)
            if order_key not in orderDict:
                orderDict[order_key] = []
            orderDict[order_key].append(order)

        # Replace the order list with a OrderList class
        orderListDict = {}
        for key, orders in orderDict.iteritems():
            orderListDict[key] = OrderList(orders)

        return orderListDict


    def extend(self, orderListToAdd):
        self.orders = self.orders + orderListToAdd.orders


    def sort(self, attribute):
        self.orders.sort(key=lambda x: getattr(x, attribute), reverse=True)


    def filter_orders_by_attribute(self, attribute, list_allowed):
        new_orders = []
        for order in self.orders:
            if getattr(order, attribute) in list_allowed:
                new_orders.append(order)

        self.orders = new_orders
        return self


    def druk_af(self):
        for order in self.orders:
            order.druk_af()


    def count(self):
        return len(self.orders)


    # Returns a copy of the OrderList for recursion.
    def copy(self):
        return OrderList(self.orders)
