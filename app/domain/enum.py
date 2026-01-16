from enum import Enum
class MainAcademicLevel(Enum):
    MainAcademicLevel1 = "التمهيدية"
    MainAcademicLevel2 = "المتوسطة"
    MainAcademicLevel3 = "التخصصية"

class CommonSubLevel(Enum):
    CommonSubLevel1 = "المستوى الأول"
    CommonSubLevel2 = "المستوى الثاني"
    CommonSubLevel3 = "المستوى الثالث"
    CommonSubLevel4 = "المستوى الرابع"

class SpecializedLevel(Enum):
    SpecializedLevel1 = "العقيدة"
    SpecializedLevel2 = "التفسير والحديث"
    SpecializedLevel3 = "الفقه وأصوله"
    SpecializedLevel4 = "اللغة العربية"
