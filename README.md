# Simple Web Crawler

## Overview

A simple web crawler that given a list of URLs it will recursively get and save in a file all <B>referred</B> emails
This is an implementation of 

## Files and folders:

- `crawler.py`: System's main, responsible for handling command line parameters, reading input file, creating shared 
    structures and firing threads.
- `worker.py`:
- `writer.py`:
- `urls.py`:
- `Dockerfile`:
- `build/requirements.txt`:
- `tests`: Simple HTML files and docker compose files to create docker swarm stacks with nginx serving the HTML files. 
   See [Testing](#testing) section) for details on how to use these. 
- `design`: PlantUML files (text-based tool for "drawing" UML diagrams) and corresponding diagrams explaining the 
   system's design. These diagrams are included in this document (with explanations) in the [Design](#design) section.
   
## Building:

### Option 1: Use docker 

To simplify dependency management a Dockerfile is provided with the code such that a self contained docker image can be easily build as follow:

`docker build -t crawler .`

The system was built and tested with docker version 18.09.7 but given the simplicity of the Dockerfile it probably works
 with older versions as well.
 
### Option 2: Python application 

For the application to run as a python script there is a need to install the BeautifulSoup4 library as follow:

`sudo pip3 install bs4`
 
## Running:

### Option 1: Use docker 

`docker run -ti -v $(pwd):/out crawler [-f <filename> | -u <url>] -o /out/<outputfile>`
 
 For a list of all supported flags type:

`docker run -ti crawler -h`
 
### Option 2: Python application 

`crawler.py  [-f <filename> | -u <url>] -o <outputfile>`

For a list of all supported flags type:

`crawler.py -h`


## Testint

`TESTS_DIR=$(pwd) docker stack deploy -c circular.yml c`

`docker run --network c_test -v $(pwd):/out crawler -u http://c1  -n 1 --verbose -o /out/<outputfile>`

## Design

### Assumptions
- In memory solution to show functionality. Should be easy to modify to a more resilient solution that uses an
  external data store
- Initial solution may not be fully optimized for performance, but desing should consider performance 
  optimizations 
- Retrieve emails only in the form of <a href='mailto:...>, while emails may appear anywhere in the text, any modern web 
  authoring tool will automatically add a link to wherever an email address is inserted, so limiting 
  the search to links will most likely find the majority of emails while greatly reducing the parsing complexity.
- Static content (more on this later)

![Components of solution](design/diagrams/crawler_obj_c4.png)

![Flowchart of Worker threads](design/diagrams/worker02.png)

## Known issues
- Unneeded fetching of non-parseable files (images, movies and such)
- Not all "local" urls seems to be properly handled (see `'Unable to categorize'` messages in logs)
- BeatifulSoup seems to have problem parsing non english text (see `' ... confidence ...'` and 
  `'... not decoded ... '` messages in logs)
- Add monitoring thread that peridically prints status (queue sizes and such)
- Limit queue size and add waiting when queue is full ?
- Add mechanism to force workers to stop ?

## Observations 
