# 4chan crawler

This repository is from live coding sessions from Binghamton University's 2024 CS 415/515 class.

## Postgres (Timescale db) install with docker

To install start up.

```
docker pull timescale/timescaledb-ha:pg16
docker run -d --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=testpassword timescale/timescaledb-ha:pg16
```

To access a psql shell:

`docker exec -it timescaledb psql -U postgres`

## sqlx migrations
if following the above, then you can use this as database url `DATABASE_URL=postgres://postgres:testpassword@localhost:5432/chan_crawler`

`sql database create`

`sql database drop`

`sqlx migrate add -r --source /path/you/want/migrations "some descriptive name"`

`sqlx migrate run`

`sqlx migrate revert`

## Faktory

Install from docker: `docker pull contribsys/faktory`

Run:

```
docker run -it --name faktory \
  -v ~/projects/docker-disks/faktory-data:/var/lib/faktory/db \
  -e "FAKTORY_PASSWORD=password" \
  -p 127.0.0.1:7419:7419 \
  -p 127.0.0.1:7420:7420 \
  contribsys/faktory:latest \
  /faktory -b :7419 -w :7420
  ```

  ## Python virtual environment

  You probably want to use virtual environments to keep evertying clean.

  `python -m venv ./env/dev`

  Activate your new environment: `source env/dev/bin/activate`

  Deactivate your environment: `deactivate`


  # Note from author
  CS 415 Social Media Data Sci Pipeline
  Group project with members: Emily Eng, Klara Veljkovic, Deepanshi Gaur, Joey Zhang
  This project was started at the start of the semester and has 3 parts to it:
  1. Creating a 4chan and Reddit continuous crawler and saving all collected data into a Postgres database (this repo)
  2. Incorporating ModerateHateSpeech API into first implementation to flag toxic posts and comments 
  3. Developing a web-based dashboard for interactive querying
  ## Limitation
  At some point in the semester, the remote desktops which were used to implement this project all got reset
  and all data was erased, so there should be more data than appears.




