import aiohttp
import asyncio
import logging
import click
from CourseraTypes import Course, Lecture, Lesson, Module, Supplement
from utils import API_URL_COURSE, API_URL_LECTURE, API_URL_MATRIAL


class Crawler:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session
        self.sem = asyncio.Semaphore(5)

    async def crawl_course(self, course_slug) -> Course:
        async with self.session.get(API_URL_COURSE(course_slug)) as resp:
            course_json = (await resp.json())['elements'][0]
        course_name = course_json['name']
        course_id = course_json['id']
        primary_language = course_json['primaryLanguageCodes']
        chosen_language = self.__choose_language(
            course_json['subtitleLanguageCodes'] + primary_language)
        ret_course = Course(course_id, course_slug, course_name,
                            primary_language, chosen_language)

        async with self.session.get(API_URL_MATRIAL(course_slug)) as resp:
            course_material_json = (await resp.json())['linked']
        id2item = {}
        crawling_tasks = []
        for item in course_material_json['onDemandCourseMaterialItems.v2']:
            type_name = item['contentSummary']['typeName']
            if type_name in ('exam', 'quiz', 'peer', 'phasedPeer', 'discussionPrompt', 'gradedProgramming', 'programming', 'ungradedWidget'):
                continue
            if type_name not in ('lecture', 'supplement'):
                logging.warning(f'unknown typename: {type_name}')
                continue
            if item.get('isLocked'):
                logging.info(f'locked item: {item["name"]}')
            if type_name == 'lecture':
                lecture = Lecture(item['id'], item['name'])
                id2item[item['id']] = lecture
                crawling_tasks.append(self.crawl_lecture(ret_course, lecture))
            elif type_name == 'supplement':
                id2item[item['id']] = Supplement(item['id'], item['name'])

        id2lesson = {}
        for lesson in course_material_json['onDemandCourseMaterialLessons.v1']:
            tmp_lesson = Lesson(lesson['id'], lesson['name'])
            for item_id in lesson['itemIds']:
                item = id2item.get(item_id)
                if item is not None:
                    tmp_lesson.add_item(item)
            id2lesson[lesson['id']] = tmp_lesson

        for module in course_material_json['onDemandCourseMaterialModules.v1']:
            tmp_module = Module(module['id'], module['name'])
            for lesson_id in module['lessonIds']:
                lesson = id2lesson.get(lesson_id)
                if lesson is not None:
                    tmp_module.add_lesson(lesson)
            ret_course.add_module(tmp_module)

        await asyncio.gather(*crawling_tasks)

    def __choose_language(self, options):
        click.echo('What language(s) do you want for subtitles?')
        click.echo('[0] no subtitle')
        for i, language_code in enumerate(options):
            click.echo(f'[{i + 1}] {language_code}')
        chosen_index = click.prompt(
            'Choose at most 2 from options above (separate with whitespace)')
        while True:
            try:
                chosen_index = [int(i) for i in chosen_index.split(' ')]
                if len(chosen_index) != 1 and len(chosen_index) != 2:
                    raise Exception()
                if 0 in chosen_index and len(chosen_index) != 1:
                    raise Exception()
                if any([x < 0 or x > len(options) for x in chosen_index]):
                    raise Exception()
            except KeyboardInterrupt:
                raise
            except:
                chosen_index = click.prompt('Invalid input, try again')
                continue
            break
        if chosen_index[0] == 0:
            return []
        return [options[i - 1] for i in chosen_index]

    async def crawl_lecture(self, course: Course, lecture: Lecture):
        async with self.sem:
            async with self.session.get(API_URL_LECTURE(course.id, lecture.id)) as resp:
                lecture_json = (await resp.json())['linked']
        video_json = lecture_json['onDemandVideos.v1'][0]['sources']['byResolution']
        subtitle_json = lecture_json['onDemandVideos.v1'][0]['subtitles']

        available_resolution = list(video_json.keys())
        highest_resolution = sorted(
            available_resolution, key=lambda x: int(x[:-1]), reverse=True)[0]
        lecture.set_url(video_json[highest_resolution]['mp4VideoUrl'])

        if all([l in subtitle_json.keys() for l in course.chosen_language]):
            lecture.set_subtitle_url([subtitle_json[l]
                                     for l in course.chosen_language])
        else:
            lecture.set_subtitle_url([subtitle_json[course.primary_language]])
