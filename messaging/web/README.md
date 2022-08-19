# spacebeaver

Space Beaver

This project was generated with [`project-boilerplate`](https://gitlab.com/softformance/lab/templates/project-boilerplate). Current template version is: [d536dd51f939b75f32eb8bf2b3d4c9225dc6798b](https://gitlab.com/softformance/lab/templates/project-boilerplate/tree/d536dd51f939b75f32eb8bf2b3d4c9225dc6798b). See what is [updated](https://gitlab.com/softformance/lab/templates/project-boilerplate/compare/d536dd51f939b75f32eb8bf2b3d4c9225dc6798b...master) since then.


## Prerequisites

You will need:

- [docker](https://docs.docker.com/engine/install/)
- [docker-compose](https://github.com/docker/compose)
- [make](https://www.man7.org/linux/man-pages/man1/make.1.html)


## Local setup

```bash
$ make up
```
This command will build and start development docker stack. It will takes a while for the first time.

*Other management command:*

* `make stop` - stop docker development containers stack and free binded ports
* `make rebuild` - stop and rebuilds docker development containers stack


## Developing locally:

Enter project directory run `make up` if stack was stopped before, otherwise just run

```
$ make shell app
```

this command will bring you to application container shell, to exit enter `exit`

Other management command:

* `make shell data` - open stack database container shell
* `make shell cache` - open stack cache container shell
* `make shell broker` - open stack broker container shell


#### Managing Django development server:
To start django development server enter application container with `make shell app`, 
make sure everything setup correctly with `make test`, and use default django commands to manage django application. 
Some shortcuts also available as make proxy commands `$ cat Makefile` will print them.

#### Managing React application:
React application located under `private` directory, so after entering application shell enter `private` directory 
and run `npm install` for the first time. Make sure everything was setup correctly with `npm test`. 
React development server can be started with `npm start`.

#### Management commands in `app shell` (`make shell app`):
* `make format` - Fix black format issues
* `make sort` - Fix import sorting issues
* `make genoutsidedb` - SqlAlchemy models generation for outside database

#### Notes:
Try run `make rebuild` and `make up` if something went wrong.

#### Testing
To run `make test` you must set `CI_PROJECT_DIR` to the project dir.
