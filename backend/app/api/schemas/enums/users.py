from enum import Enum


class LmsRole(str, Enum):
    STUDENT = "Ученик"
    PARENT = "Родитель"
    TEACHER = "Учитель"
    REPRESENTATIVE = "Представитель учреждения"

class GenderRole(str, Enum):
    MALE = "Мужской"
    FEMALE = "Женский"

