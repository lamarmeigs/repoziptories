# repoziptories
This project aims to implement a RESTful API that merges profile data from [GitHub](https://github.com) and [BitBucket](https://bitbucket.org). Per the preferred requirements, it will run on Flask and Python 3.6.

## Usage
Prior to running this application, please note the following prerequisites:

  - [Pipenv](https://pipenv.readthedocs.io/en/latest/) must be installed
  - Python 3.6 must be installed
  - A [GitHub Personal Access Token](https://github.com/settings/tokens) should be added to the `config/config.yaml` file

That done, running the application is as simple as executing the following commands:
```bash
$ pipenv install
$ pipenv shell
$ python run.py
```

## Changelog
### Version 1.0
  - A single endpoint exists: `GET /v1/profile/{username}`
    - An account corresponding to the given username will be sought in both GitHub and BitBucket.
    - The collated results are returned in a JSON object (note: this may take a while).
    - Missing accounts are ignored.
    - Any rate limiting or bad credentials will result in failure.

