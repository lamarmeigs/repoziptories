def merge_profiles(github_profile, bitbucket_profile):
    """Aggregate the data of the given profiles.

    Args:
        github_profile (dict): the data returned from
            clients.github.GithubClient.get_profile
        bitbucket_profile (dict): the data returned from
            clients.github.BitBucketClient.get_profile

    Return:
        a dict represented the merged profile data
    """
    merged_profile = {
        'repositories': {
            'original': 0,
            'forked': 0,
        },
        'stars': 0,
        'issues': 0,
        'languages': [],
        'topics': [],
        'followers': 0,
        'following': 0,
        'starred': 0,
    }

    # total number of public repos (seperate by original repos vs forked repos)
    # total watcher/follower count
    # total number of stars recieved
    # total number of stars given
    # total number of open issues
    # total number of commits to their repos (not forks)
    # total size of their accounts
    # a list/count of langagues used
    # a list/count of repo topics
