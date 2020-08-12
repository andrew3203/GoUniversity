from classes.direction import Direction


class University:

    def __init__(self, data):
        self.id = data[0]
        self.short_name = data[1]
        self.full_name = data[2]
        self.site = data[3]

        self.university_type = data[4]
        self.user_id = data[5]

        self.directions = {
                    'directions_short_name': Direction()
                }

    def set_values(self, *kwargs):
        pass

    def insert_to_db(self):
        pass



