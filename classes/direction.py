import psycopg2


class Direction:

    def __init__(self, data):
        self.id = data[0]
        self.short_name = data[1]
        self.full_name = data[2]

        self.about_link = data[3]
        self.data_link = data[4]
        self.direction_type = data[5]

        self.applicant_came = data[6]
        self.applicant_limit = data[7]
        self.originals_came = data[8]

        self.unsname = data[9]

    def set_values(self, *kwargs):
        pass

    def get_info(self):
        pass

    def insert_to_db(self):
        pass
