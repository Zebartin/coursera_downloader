from typing import List
from utils import formatted_file_name, URL_ROOT

PREFIX = '    '


class Item:
    def __init__(self, course_id, item_id, name) -> None:
        self.id = f'{course_id}~{item_id}'
        self.name = formatted_file_name(name)

    def __str__(self) -> str:
        return self.name

    @property
    def type_name(self) -> str:
        return type(self).__name__


class Lecture(Item):
    def set_url(self, url: str) -> None:
        self.url = url

    def set_subtitle_url(self, urls: List[str]) -> None:
        self.subtitle_url = [URL_ROOT + u for u in urls]

    @property
    def file_name(self) -> str:
        return self.name + '.mp4'

    @property
    def subtitle_name(self) -> str:
        return self.name + '.srt'


class Supplement(Item):
    @property
    def file_name(self) -> str:
        return self.name + '.html'


class Lesson:
    def __init__(self, lesson_id, name) -> None:
        self.id = lesson_id
        self.name = formatted_file_name(name)
        self.items: List[Item] = []

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def __str__(self) -> str:
        return '\n'.join([self.name] + [PREFIX + str(i) for i in self.items])


class Module:
    def __init__(self, module_id, name) -> None:
        self.id = module_id
        self.name = formatted_file_name(name)
        self.lessons: List[Lesson] = []

    def add_lesson(self, lesson: Lesson) -> None:
        self.lessons.append(lesson)

    def __str__(self) -> str:
        return '\n'.join([self.name] + [PREFIX + line for l in self.lessons for line in str(l).split('\n')])


class Course:
    def __init__(self, course_id, course_slug, name, primary_language, chosen_language) -> None:
        self.id = course_id
        self.slug = course_slug
        self.name = formatted_file_name(name)
        self.primary_language = primary_language
        self.chosen_language = chosen_language
        self.modules: List[Module] = []

    def add_module(self, module: Module) -> None:
        self.modules.append(module)

    def __str__(self) -> str:
        return '\n'.join([self.name] + [PREFIX + line for m in self.modules for line in str(m).split('\n')])


class Specification:
    def __init__(self, spec_id, spec_slug, name) -> None:
        self.id = spec_id
        self.slug = spec_slug
        self.name = formatted_file_name(name)
        self.courses: List[Course] = []

    def add_course(self, course: Course) -> None:
        self.courses.append(course)
