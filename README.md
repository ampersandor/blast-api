## BlastAPI 1.0.0

![image](https://github.com/ampersandor/blast-api/assets/57800485/e8855644-fb97-4a62-8fef-ec965692c31a)


<details>
    <summary>Table of content</summary>

- [About](#about)
- [Getting-Started](#getting-started)
    - [Prerequisite](#prerequisite)
    - [Installation](#installation)
- [License](#license)
- [Contact](#contact)
- [Links](#links)    
</details>

## Overview
**BlastAPI** is a robust and scalable API built using FastAPI to handle user requests for BLAST (Basic Local Alignment Search Tool) operations. It leverages a microservices architecture with RabbitMQ for message queuing and Redis for caching to ensure high performance and reliability.

## Features
FastAPI: Provides a modern and high-performance web framework for building APIs.  
RabbitMQ: Acts as a message broker, allowing asynchronous processing and communication between services.  
Redis: Used for caching to speed up repeated queries and improve the overall performance.


## Getting Started
### Prerequisite
* blastn (2.15.0)  
    * https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.15.0/ncbi-blast-2.15.0+.dmg
* python (3.12.3)
* poetry (1.8.3)
* docker (version 24.0.2, build cb74dfc)
    * rabbitmq service (docker container)
        ```bash
        docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management &
        ```
    * redis service (docker container)
        ```bash
        docker run -p 6379:6379 --name docker_redis redis
        ```

### Installation
```bash
git clone https://github.com/ampersandor/blast-api.git
cd blast-api
poetry shell
poetry install
```

### How to use
```bash
# Run the fastAPI server
python3 gateway/main.py &

# Run the blast-service
python3 blast-services/main.py &

# Send request to the API
python3 clinet/client.py

```

## Contact

DongHun Kim - <ddong3525@naver.com>
