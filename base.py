class Class:

    def __init__(self, groups, professor, subject, type, duration, classrooms):
        self.groups = groups
        self.professor = professor
        self.subject = subject
        self.type = type
        self.duration = duration
        self.classrooms = classrooms

    def __str__(self):
        return "Groups {} | Professor '{}' | Subject '{}' | Type {} | {} hours | Classrooms {} \n"\
            .format(self.groups, self.professor, self.subject, self.type, self.duration, self.classrooms)

    def __repr__(self):
        return str(self)


class Classroom:

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        return "{} - {} \n".format(self.name, self.type)

    def __repr__(self):
        return str(self)


class Data:

    def __init__(self, groups, professors, classes, classrooms):
        self.groups = groups
        self.professors = professors
        self.classes = classes
        self.classrooms = classrooms
