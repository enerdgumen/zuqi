# Zuqi

Zuqi (anagram of "Quiz") is a turn-based demostrative game written in Python and JavaScript.

The backend is powered by [aiohttp](https://github.com/aio-libs/aiohttp),
the frontend is a browser application based on [React](https://reactjs.org/) and [Material UI](https://material-ui.com/).

A live demo is available on Heroku at [https://zuqing.herokuapp.com](https://zuqing.herokuapp.com/).

## Project structure

* *conductor*: the backend server;
* *webapp*: the frontend web application.

Consult the specific README of each module for more details.

## Build and run with Docker

```
docker build -t zuqi .
docker run -p 8000:80 zuqi
```