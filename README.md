# Timeit

## Overview

This is a service that will spawn timers, which will then trigger a webhook after the specified interval.

## Design

### Architecture

There are two main services in this application: a Timer Ingestion service and a Scheduler service. The Timer Ingestion service is a RESTful API (based on the [Flask](https://flask.palletsprojects.com/en/2.0.x/) framework) which accepts a new timer job definition. This is then processed and saved in a noSQL store (MongoDB), and also pushed to a queue (RabbitMQ). 

The Scheduler service consumes new messages from the queue, and schedules jobs based on the expiry time specified in the message (using the [APScheduler](https://apscheduler.readthedocs.io/en/3.x/) library). The Scheduler service also persists these jobs in the database (MongoDB), so that they can be resumed in the case of a reboot.

### Data Model

Since we really only care about the expiry time for a particuler timer job, we can compute the expiry time based on the request receipt time. Therefore, we can define a `Timer` entity as:

```
Timer:
----------------------
id: UUID
expiry_time: Integer
url: URL
```

Furthermore, this data is not strongly relational. Therefore, we can go with a NoSQL solution, which also has the added benefit of easy horizontal scalability, should we need it.

### RESTful API

This REST API will allow for two operations:
* Set Timer
```sh
POST /api/v1/timers

Request Schema
{
    "hours": int,
    "minutes": int,
    "seconds": int,
    "url": URL string
}

Response Schema
{
    "id": UUID
}
```
* Get Timer by ID
```sh
GET /api/v1/timers/<uuid:id>

Response Schema
{
    "id": UUID
    "time_left": int
}
```

## Running

This project has been containerized. There is a helper script called `run.sh`. The application can be run via
```sh
./run.sh
```

This will then launch the MongoDB and RabbitMQ containers (these containers will NOT be exposed outside of the internal Docker network), after which it will launch the API (broadcasting on :8000) and scheduler containers. Both MongoDB and RabbitMQ containers are also volume mounted to the host, so even if the whole application goes down, the application will be able to retain data on next boot.