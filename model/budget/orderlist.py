class OrderList:
    orders = []  # List of orders

    def __init__(self, orders=None):
        if orders is None:
            orders = []
        self.orders = orders


    def split(self, attributes_to_group):
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
        order_list_dict = self.__split(attributes_to_group.pop(0))

        if attributes_to_group:
            for key, orderListDictChild in order_list_dict.iteritems():
                order_list_dict[key] = orderListDictChild.split(
                    list(attributes_to_group))  # list(..) creates a copy for recursion!

        return order_list_dict

    def __split(self, attribute_to_group):
        order_dict = {}
        # Sort out orders for each attribute to group
        for order in self.orders:
            order_key = getattr(order, attribute_to_group)
            if order_key not in order_dict:
                order_dict[order_key] = []
            order_dict[order_key].append(order)

        # Replace the order list with a OrderList class
        order_list_dict = {}
        for key, orders in order_dict.iteritems():
            order_list_dict[key] = OrderList(orders)

        return order_list_dict


    def extend(self, order_list_to_add):
        self.orders = self.orders + order_list_to_add.orders


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


    """
        Input: None
        Output: ordernummers as a list of ints
    """
    def ordernummers(self):
        ordernummers = []
        for order in self.orders:
            ordernummers.append(int(order.ordernummer))
        return ordernummers

