import aiohttp
import asyncio
import click
import os
import logging
from typing import List
from CourseraTypes import Course, Lecture, Supplement
from utils import API_URL_SUPPLEMENT


class Downloader:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session
        self.max_retry = 5
        self.sem = asyncio.Semaphore(3)

    async def download_course(self, course: Course, saving_path: str):
        click.echo('Downloading...')
        downloading_tasks = []
        for i, module in enumerate(course.modules):
            for j, lesson in enumerate(module.lessons):
                lesson_path = os.path.join(
                    saving_path, course.name, f'{i + 1:02} {module.name}', f'{j + 1:02} {lesson.name}')
                os.makedirs(lesson_path, exist_ok=True)
                for k, item in enumerate(lesson.items):
                    full_path_prefix = os.path.join(lesson_path, f'{k+1:02} ')
                    if item.type_name == 'Lecture':
                        downloading_tasks.append(
                            self.download_lecture(item, full_path_prefix))
                    elif item.type_name == 'Supplement':
                        downloading_tasks.append(
                            self.download_supplement(item, full_path_prefix))

        with click.progressbar(asyncio.as_completed(downloading_tasks), length=len(downloading_tasks), show_eta=False, show_pos=True) as bar:
            for task in bar:
                await task

    async def download_lecture(self, lecture: Lecture, saving_path_prefix: str):
        await self.__download_lecture_video(lecture, saving_path_prefix)
        await self.__download_lecture_subtitle(lecture, saving_path_prefix)

    async def __download_lecture_video(self, lecture: Lecture, saving_path_prefix: str):
        saving_path = saving_path_prefix + lecture.file_name
        if os.path.exists(saving_path):
            return
        while True:
            async with self.sem:
                async with self.session.get(lecture.url) as resp:
                    with open(saving_path, 'wb') as f:
                        retry = self.max_retry
                        while retry > 0:
                            try:
                                chunk = await resp.content.readany()
                            except KeyboardInterrupt:
                                logging.warning('Interrupted')
                                f.close()
                                os.remove(saving_path)
                                raise
                            except:
                                retry -= 1
                                continue
                            if len(chunk) == 0:
                                break
                            f.write(chunk)
                            retry = self.max_retry
                        else:
                            os.remove(saving_path)
                            continue
            break

    async def __download_lecture_subtitle(self, lecture: Lecture, saving_path_prefix: str) -> None:
        saving_path = saving_path_prefix + lecture.subtitle_name
        if os.path.exists(saving_path) or len(lecture.subtitle_url) == 0:
            return
        subtitles = []
        for i in lecture.subtitle_url:
            async with self.sem:
                async with self.session.get(i) as resp:
                    subtitles.append(await resp.text())
        merged_subtitle = self.__merge_subtitles(subtitles)
        with open(saving_path, 'w', encoding='utf-8') as f:
            f.write(merged_subtitle)

    def __merge_subtitles(self, subtitles: List[str]) -> str:
        if len(subtitles) == 1:
            return subtitles[0]
        splitted_subtitles = [s.split('\n\n') for s in subtitles]
        # do not merge subtitles with different length
        if len(splitted_subtitles[0]) != len(splitted_subtitles[1]):
            return subtitles[0]
        merged = []
        for i in range(len(splitted_subtitles[0])):
            parts = splitted_subtitles[0][i].split('\n', 2)
            # empty line
            if len(parts) == 2:
                continue
            parts.append(splitted_subtitles[1][i].split('\n', 2)[2])
            merged.append('\n'.join(parts))
        return '\n\n'.join(merged)

    async def download_supplement(self, supplement: Supplement, saving_path_prefix: str):
        saving_path = saving_path_prefix + supplement.file_name
        if os.path.exists(saving_path):
            return
        async with self.sem:
            async with self.session.get(API_URL_SUPPLEMENT(supplement.id)) as resp:
                renderableHtml = (await resp.json())['linked']['openCourseAssets.v1'][0]['definition']['renderableHtmlWithMetadata']['renderableHtml']
        with open(saving_path, 'w') as f:
            f.write(renderableHtml)
