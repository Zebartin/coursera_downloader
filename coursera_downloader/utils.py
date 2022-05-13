import platform

URL_ROOT = 'https://www.coursera.org'


def API_URL_SPEC(slug):
    return f'{URL_ROOT}/api/onDemandSpecializations.v1?q=slug&slug={slug}&fields=courseIds'


def API_URL_COURSE(slug, course_id=None):
    if slug:
        return f'{URL_ROOT}/api/onDemandCourses.v1?q=slug&slug={slug}'
    return f'{URL_ROOT}/api/onDemandCourses.v1/{course_id}'


def API_URL_MATRIAL(slug):
    return f'{URL_ROOT}/api/onDemandCourseMaterials.v2/?q=slug&slug={slug}&includes=modules,lessons,items&fields=moduleIds,onDemandCourseMaterialModules.v1(name,slug,description,timeCommitment,lessonIds,optional,learningObjectives),onDemandCourseMaterialLessons.v1(name,slug,timeCommitment,elementIds,optional,trackId),onDemandCourseMaterialItems.v2(name,slug,timeCommitment,contentSummary,isLocked,lockableByItem,itemLockedReasonCode,trackId,lockedStatus,itemLockSummary)&showLockedItems=true'


def API_URL_LECTURE(item_id):
    return f'{URL_ROOT}/api/onDemandLectureVideos.v1/{item_id}?includes=video&fields=onDemandVideos.v1(sources,subtitles)'


def API_URL_SUPPLEMENT(item_id):
    return f'{URL_ROOT}/api/onDemandSupplements.v1/{item_id}?includes=asset&fields=openCourseAssets.v1(typeName),openCourseAssets.v1(definition)'


def formatted_file_name(file_name: str):
    for c in '<>:"/\|?*':
        file_name = file_name.replace(c, '')
    return file_name
