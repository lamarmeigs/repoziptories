from collections import defaultdict


def merge_profiles(*profiles):
    """Aggregate the data of the given SCM profiles"""
    merged_profile = defaultdict(int)
    merged_profile['repositories'] = defaultdict(int)
    count_fields = ('stars', 'starred', 'issues', 'followers', 'following', 'commits')
    languages = set()
    topics = set()
    for profile in profiles:
        if not profile:
            continue

        for field in count_fields:
            merged_profile[field] += profile.get(field, 0)

        languages.update(profile.get('languages', []))
        topics.update(profile.get('topics', []))

        repositories = profile.get('repositories')
        if isinstance(repositories, int):
            merged_profile['repositories']['original'] += repositories
        elif isinstance(profile.get('repositories'), dict):
            merged_profile['repositories']['original'] += repositories.get('original', 0)
            merged_profile['repositories']['forked'] += repositories.get('forked', 0)

    merged_profile.update({
        'languages': list(languages),
        'topics': list(topics),
    })
    return dict(merged_profile)
