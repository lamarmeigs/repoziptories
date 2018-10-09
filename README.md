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
### Version 1.1
  - Updates `GET /v1/profile/{username}` to accept overriding usernames:
    - `?github_username`: will be used instead of `username` when retrieving GitHub profile data
    - `?bitbucket_username`: will be used instead of `username` when retrieving BitBucket profile data
    - `?bitbucket_team`: indicates either the BitBucket profile is that of a team or an individual user

### Version 1.0
  - A single endpoint exists: `GET /v1/profile/{username}`
    - An account corresponding to the given username will be sought in both GitHub and BitBucket.
    - The collated results are returned in a JSON object (note: this may take a while).
    - Missing accounts are ignored.
    - Any rate limiting or bad credentials will result in failure.


## To Do:
  - Concurrency

      Both client classes have to send multiple requests to gather all needed profile data. Running all requests sequentially causes unnecessary delays. Instead, the application can streamline its behavior by retrieving separate data concurrently, either individual requests (via a library like [`requests-futures`](https://github.com/ross/requests-futures)) or separate client methods.

  - Caching

      While requesting data concurrently may reduce some delays, there is no circumventing the latency inherent to rederiving information on demand. The prohibitive wait times can be effectively removed by caching information in a datastore like Redis. Depending on the use case, the application should either cache the assembled profile data (for simplicity) or the responses to individual resquests (for better fine-tuning).

  - Full REST Interface

      While the singular GET endpoint is sufficient for an initial prototype, it provides only a limited concept of a "merged user profile" resource (and doesn't persist data, beyond the caching suggested above). Ideally, it should provide storage for a Profile record (composed of a generic username, a GitHub username, and a BitBucket username), and expose the following endpoints:
      - `GET /profile`: retrieves a paginated list of Profile records
      - `GET /profile/{username}`: returns the specified profile, along with merged GitHub & BitBucket data
      - `POST /profile`: creates a new Profile record
      - `PATCH /profile/{username}`: updates the specified profile
      - `DELETE /profile/{username}`: deletes the specified profile
