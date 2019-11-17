# Know Issues:

## Unable to Categorize/Classify

How can we identify non-parseable resources without hints in the url itself
Example of the problem:

`https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=en-US`

points to binary `firefox-70.0.1.tar.bz2` but no indication of it in the url


## maxdepth

Currently when one thread reaches maxdepth, the program exists and
kills all workers still active. 

- Does it makes sense to let them all finish?
- If not, should workers be properly stopped (like writer) so they finish with the 
url processing currently in progress 

## Stucked at the end

With no maxdepth there is a chance, that all workers are waiting for new urls
but no one is pushing them, kind of a deadlock.

- Use timeouts ?
- Enable to add more input urls to running system ?
- ???




