from telegram.ext import BaseFilter


class KeyboardFilter(BaseFilter):
    def filter(self, message):
        if message.text in ['Book', 'Feedback', 'Join', 'Order', 'CheckOut', 'Info', 'Wait']:
            return True
        else:
            return False


class KeyRestaurantFilter(BaseFilter):
    def __init__(self, restaurants):
        self.restaurants = [r.lower().strip() for r in restaurants]

    def filter(self, message):
        key_restaurant = message.text
        if key_restaurant.lower().strip() in self.restaurants:
            return True
        else:
            return False


class PeopleFilter(BaseFilter):
    def filter(self, message):
        try:
            int(message.text)
            return True
        except:
            return False


class EmailFilter(BaseFilter):
    def filter(self, message):
        email = message.text
        if '@' in email and email.endswith(('.it', '.com', '.eu')):
            return True
        else:
            return False
