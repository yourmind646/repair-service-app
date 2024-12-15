from models.user import User


class Booking:
	def __init__(self, user: User, service):
		self.user = user
		self.service = service

	def process_booking(self):
		cost = self.service.get_cost()
		discount = self.user.get_membership_discount()
		discount_amount = cost * discount
		cost -= discount_amount
		return cost
