# Know Issues:

## Unable to Categorize/Classify

How can we identify non-parseable resources without hints in the url itself
Example of the problem:

`https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=en-US`

points to binary `firefox-70.0.1.tar.bz2` but no indication of it in the url

The extension approach is clearly not good, instead need to fetch content-type, preferably
without fetching the entire resource. 

`urllib.request.urlopen('<URL>').info.get_content_type()` ???

```python
import urllib.request
with urllib.request.urlopen('http://www.google.com') as response:
    info = response.info()
    print(info.get_content_type())      # -> text/html
    print(info.get_content_maintype())  # -> text
    print(info.get_content_subtype())   # -> html
```

## maxdepth

Currently when one thread reaches maxdepth, the program exists and
kills all workers still active. 

- Does it makes sense to let them all finish?
- If not, should workers be properly stopped (like writer) so they finish with the 
url processing currently in progress - YES, otherwise we may lose emails already found

## Stucked at the end

With no maxdepth there is a chance, that all workers are waiting for new urls
but no one is pushing them, kind of a deadlock.

- Use timeouts ?
- Enable to add more input urls to running system ?
- ???




