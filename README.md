# Fenrir

### Requirements

 - Python 3
 - Pip

### Setup

run ``pip install -r requirements.txt``

### Usage

#### Mining mode usage  
  
``` 
usage: Mining.py [-h] url path n step

positional arguments:
  url         git url of your android project
  path        Path where clones will be store.
  n           Number of clone
  step        Step of commit between each clone

optional arguments:
  -h, --help  show this help message and exit
```
#### Analyse mode usage  
  
``` 
usage: Analyse.py [-h] [-apk] path out

positional arguments:
  path        Path where clones are stored
  out         output path

optional arguments:
  -h, --help  show this help message and exit
  -apk        if set program will except only apk in path
```

#### Render mode usage  (Deprecated use JavaFx render)
  
``` 
usage: Render.py [-h] [-progress] [-sameClass] [-sameFunc] path out

positional arguments:
  path        Path of the out.txt
  out         output path

optional arguments:
  -h, --help  show this help message and exit
  -progress   plot of the anti pattern progression
  -sameClass  print location by class where they are several anti patterns
  -sameFunc   print location by class where they are several anti patterns
```

### Exemple

 - Get 4 clones of repo url.git with 100 commits beetwen each clone and store them in ReposPath
`python3.6 ./Mining.py url.git ReposPath 4 100`

 - Analyse clones in ReposPath and store the result in OutPath
`python3.6 ./Analyse.py ReposPath OutPath`

