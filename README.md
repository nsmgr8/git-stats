# Source Code Statistics Generator and Viewer

Here we have a source code statistics generator and web viewer. A list of
project maintained in git VCS can be looked into to generate some statistics.
These statistics can then be viewed on browser when deployed in a webserver.

# Requirements

0. Linux or MacOS
1. Python 3.6+ (https://www.python.org/)
2. NodeJS 8+ (https://nodejs.org/en/)
3. Yarn 1.6+ (https://yarnpkg.com/lang/en/)

Use your preferred installation method to install the above requirements.

# Installation

Clone this repository to your machine, say in `/var/www/git-stats`.

    $ git clone https://github.com/nsmgr8/git-stats.git
    $ cd git-stats/ngapp
    $ yarn build

## Configuration

The list of projects that it should generate statistics for are listed in
config.ini file in the root of this project. That is, in this case
`/var/www/git-stats/config.ini`. An example config.ini file is provided in that
location. Copy that file and make changes as following:

    $ cd /var/www/git-stats
    $ cp config.ini.example config.ini
    $ $EDITOR config.ini

There are two sections in the config file `GLOBAL` and `REPOSITORIES`.

### GLOBAL

In the global section we will configure some options that stats generator can
use. Currently these are:

- **workdir**: The working directory for the stats generator. In this folder,
    the stats generator will clone all the projects in `repos` folder and then
    store stats data in `data` folder. This `data` folder contains all stats
    per project in multiple JSON files. This data folder should also be served
    by the webserver at `/data/`.

- **detect_move**: When generating lines count per author, by default the lines
    are counted by last commit info. If `detect_mode` is specified then it will
    try to find the original commit info for lines. It's a space separated
    project ids. Note that, this is an expensive operation. It can take weeks
    for big projects to get this data.

- **process_pool**: By default, the generator uses multiprocesses as much as
    the number of CPUs available. If you'd like to decrease the process
    numbers, use this to specify how many processes you would like.


### REPOSITORIES

In this section, you need to provide the list of your projects that you want to
get statistics for. Each project has an ID, and three URLs for clone, browse
and website. ID and clone URL are required, browse and website URLs are
optional. The format is as follows:

    [REPOSITORIES]
    project_one =
        clone: ssh://url/to/clone/the/project/one
        web: http://url/to/browser/the/code/
        site: http://url/to/the/corresponding/website/say/deployment

# Generate Statistics

Once the `config.ini` file is populated, run the generator to get all the
statistics.

    $ cd /var/www/git-stats
    $ python3 -m gitstats -v

This will clone the projects to the workdir specified in the GLOBAL section of
config.ini and start populating stats JSON files.

You may use a crontab entry to run this periodically to update the project
stats.

# Webserver Example (nginx)

Once the generation of JSON statistics files (`python3 -m gitstats`) and
webpage build (`yarn build`) are done. One can configure nginx to serve the
statistics viewer via nginx as follows.

Serve webpage build at / and json files root at /data/. That is,

    location / {
        root /var/www/git-stats/ngapp/dist/ngapp;
        try_files $uri /index.html;
    }

    location /data/ {
        root /var/www/git-stats/workdir;
    }

An example nginx config is provided in `gitstats.nginx.conf` file.
