# Simple Web Crawler

## Overview

A simple web crawler that given a list of URLs it will recursively fetch resources and extract from them all <B>referred</B> emails.
## Files and folders:

- `crawler.py`: System's main, responsible for handling command line parameters, reading input file, creating shared 
    structures and firing threads.
- `worker.py`: Code for the "worker" threads, i.e., the threads doing the heavy lifting of the crawling process:
   fetch, parse and search
- `writer.py`: Code for the thread responsible for writing the list of emails found to the output file
- `urls.py`: Classes for URL objects. To simplify the code of the workers, each category of URLs (email, webpage, unknow) gets a dedicated class 
   for handling the corresponding URLs.
- `Dockerfile`: Use to build the crawler container
- `build/requirements.txt`: Python dependencies. Used by Dockerfile to build container
- `tests`: Simple HTML files and docker compose files to create docker swarm stacks with nginx serving the HTML files. 
   See [Testing](#testing) section) for details on how to use these. 
- `design`: PlantUML files (text-based tool for "drawing" UML diagrams) and corresponding diagrams explaining the 
   system's design. These diagrams are included in this document (with explanations) in the [Design](#design) section.
- `runs`: Folder used to collect input, output and log files from different runs of the system. The comments in the
   [Observations](observations) section refers to these files.
## Building:

### Option 1: Use docker 

To simplify dependency management a Dockerfile is provided with the code such that a self contained docker image can be 
easily build as follow:

`docker build -t crawler .`
 
### Option 2: Python application 

For the application to run as a python script there is a need to install the BeautifulSoup4 library as follow:

`sudo pip3 install bs4`
 
## Running:

### Option 1: Use docker 

`docker run -d -v $(pwd):/<guestdir> crawler [-f <filename> | -u <url>] -o /<guestdir>/<outputfile>`
 
 Please note that it is important to pass the volume parameter (`-v <hostdir>:<guestdir>), without it the resulting output
 file (and logs) will only be available in the container's file system
  
 For a list of all supported flags type:

`docker run -ti crawler -h`
 
### Option 2: Python application 

`python3 crawler.py  [-f <filename> | -u <url>] -o <outputfile>`

For a list of all supported flags type:

`python crawler.py -h`

### Supported flags (applicable to both options above):

- `-i <filename>, --input <filename>`:
- `-u <URL>, --url <URL>`:
- `-o <filename>, --output <filename>`:
- `-n #, --nthreads #`: [Optional] Number of threads. Default: 10
- `--maxdepth`: [Optional] Maximum depth to crawl. Default: no limit
- `--verbose` : [Optional] Maximize logs generated (show all logs)
- `--quiet` : [Optional] Minimize logs generated (only critical errors)
- `--logfile <filename>`: [Optional] If present logs are saved to <filename>, otherwise to stout/stderr.
- `-h`: Shows short help message


## Testing

To validate correctness we need to run the system on set of web pages such that the expected results are known. To this
end, a couple of docker swarm stacks are provided. With these stacks, we can easily bring up a set of local web servers with
controlled content.

To deploy the stacks, docker swarm needs to be enabled as follow:

`docker swarm init`

then, the testing web servers can be deployed with the `docker stack deploy -c <stack.yml> command.

### Circular test

The stack in `tests\circular.yml` enables us to test 1. that the system will not enter into an infinite loop, and 2.
only unique emails are saved. It consists of 3 web servers, each with a simple HTML page that point to the next server; 
the HTML in the last server points back to the first one, thus creating a loop. In addition, in the HTML of each server
there is a list of email references, but only one is unique.

To deploy the stack, type (while in the crawler directory):

`TESTS_DIR=$(pwd)/tests docker stack deploy -c tests/circular.yml c`

the run the crawler container as follow:

`docker run --network c_test -v $(pwd)/runs:/tmp crawler -u http://c1 --verbose -o /tmp/circular.out --logfile /tmp/circular.log`

For this to work properly, the network parameter (`--network c_test`) is a must. It connects the crawler to the `c_test`
virtual network and the associated namespace (swarm internal DNS server resolved the hostname `c1` if accessed in the `c_test` 
network)

### Multi-page test

`TESTS_DIR=$(pwd) docker stack deploy -c tests/multipage.yml m`

`docker run -d --name crawler --network m_test -v $(pwd)/runs:/out crawler -u http://m1 -o /out/multipage.txt --logfile /out/multipage.log --verbose`


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

![Components of solution](design/diagrams/crawler_obj_current.png)

![Worker flowchart](design/diagrams/worker01.png)


![Simplified Worker flowchart](design/diagrams/worker02.png)

### Proposed improvements

The single process, all in-memory, python implementation is good as a proof of concept, it not well suited for a 
production system. However, with minor changes to the code and the deployment model, with the same basic design we 
achieve a much robust, scalable and better performing system.

#### Suggested changes (system-wide):
1. Use standalone processes instead of python Threads. Each such process can be packaged as a container
2. Replace python queues with a standalone distributed queuing system, such as `RabbitMQ` or `Kafka`,
3. Replace python dictionaries with a standalone key-value-store system, such as `Redis` or `Memcached`

With these changes in place the system is now made of several service layers (see modified object diagram below), where 
each service can be deployed, scaled and managed independently. For maximum performance, scalability
and availability, this improved system can be easily deployed on a large cluster managed by a 
container orchestration system such as `kubernetes`.    

#### Additional improvements (local):
1. Consider better performing alternatives to `BeautifulSoup` as the parser
2. Download/fetch only parseable resources (i.e, text based files such as HTML, XML)
3. Redesign to support dynamic content


![Components of proposed solution](design/diagrams/crawler_obj_proposed.png)

## Known issues
- Unneeded fetching of non-parseable files (images, movies and such)
- Not all "local" urls seems to be properly handled (see `'Unable to categorize'` messages in logs)
- BeatifulSoup seems to have problem parsing non english text (see `' ... confidence ...'` and 
  `'... not decoded ... '` messages in logs)
- Add monitoring thread that peridically prints status (queue sizes and such)
- Limit queue size and add waiting when queue is full ?
- Add mechanism to force workers to stop ?

## Observations 

From looking at the results after running the system a few times we can get a feeling of what needs further work.
If we look at the numbers:

`[1]$ grep working *.log | wc -l`
`97742`
`[2]$ wc -l *.out`
` 164 total`
`[3]$ grep fetch *.log | wc -l`
`4277`
`[4]$ grep parse *.log | wc -l`
`3009`
`[5]$ grep categorize *.log | wc -l`
`8198`

From these numbers, we can reach the following conclusions:

1. The use of the `mailto` reference tag is not too common (164 out of almost 10K). Need to revisit the assumption that 
the `mailto` tag will get most of the email addresses

2. Error rate is too high - around 15% (8198+3009+4277). From these errors, 3% will go away if code fetch only
 parseable resources; 4% are probably due to network errors or stale URLs; the remaining 8% is what I labeled as 
 'categorize error' which points to "local references" where the means the URL was not fully qualified and I try to
  build a fully qualified URL from the  at hand (the previous URL). This code needs to be revised to see if we can get 
  better results (less categorize errors).

Another interesting observation is that one of the runs worked on considerable less URLs that the other but both run about the same time (around 1 hour)
and with the same resources (the default 10 threads):

`[6]$ grep working list1.log | wc -l`
`55585`
`[7]$ grep working list2.log | wc -l`
`4130`

By looking at the logs of the "lazy" run we can see that the system is waiting on the download of un-parseable large files (
(linux distributions in this case). Code to avoid this will greatly improve performanace:

`
[8]$ grep working list2.log | tail 
DEBUG: W#00009 working on [http://www.kick.co.il]
DEBUG: W#00009 working on [https://www.vesty.co.il]
DEBUG: W#00009 working on [None]
DEBUG: W#00009 working on [None]
DEBUG: W#00009 working on [https://download.mozilla.org/?product=firefox-stub&os=win64&lang=en-US]
DEBUG: W#00005 working on [https://download.mozilla.org/?product=firefox-msi-latest-ssl&os=win64&lang=en-US]
DEBUG: W#00009 working on [https://download.mozilla.org/?product=firefox-stub&os=win&lang=en-US]
DEBUG: W#00009 working on [https://download.mozilla.org/?product=firefox-msi-latest-ssl&os=win&lang=en-US]
DEBUG: W#00009 working on [https://download.mozilla.org/?product=firefox-latest-ssl&os=osx&lang=en-US]
DEBUG: W#00005 working on [https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=en-US]
`


