class Parent_category:
	children = []

	def __init__(self, id, name):
		self.id = id
		self.name = name

	def add_child(self, child_category):
		self.children.append(child_category)

	def __str__(self):
		return(f"{self.id} {self.name}")
