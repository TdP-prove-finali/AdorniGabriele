class User:
    def __init__(self, id, name, surname, age, weight, gender, activity, goal):
        self._id = id
        self._name = name
        self._surname = surname
        self._age = age
        self._weight = weight
        self._gender = gender
        self._activity = activity
        self._goal = goal

        self._mre = None
        self._tdee = None


    def __str__(self):
        return f"{self._name} {self._surname}"

    def __hash__(self):
        return hash(self._id)



