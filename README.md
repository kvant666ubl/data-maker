# data-maker
Multi-operating tool for make custom dataset  

## Usage

### Basic commands:
```sh
$ python3 main.py --help
Usage: main.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  arrange
  aug
  datamake
  download
  resize
```

### Resize images in dataset with ``'h,w'``

#### Resize all images in 'FirearmDataset/pistols/' directory to 320x240:
```sh
python3 main.py resize --path=FirearmDataset/pistols/ --size='320,240'
```


### Download images
```sh
$ python3 main.py download --help
Usage: main.py download [OPTIONS]

Options:
  -p, --pattern TEXT        Search pattern ('ak47', 'mp5')
  -w, --webdriver TEXT      Webdriver ('gecko', 'chrome')
  -s, --size TEXT           Image size which specified manually ('large',
                            'medium', 'icon')
  -n, --number INTEGER      Number of images to download
  -c, --csplit BOOLEAN      Enable splitting download images into pattern
                            classes in download folder
  -p, --unique BOOLEAN      Enable unique images name using hash lib
  -p, --path TEXT
  -a, --plist TEXT          Path to pattern list text file
  -g, --gui
  -t, --threads INTEGER     Number of threads
  -u, --unverified BOOLEAN  Disable unverified HTTPS request
                            (InsecureRequestWarning, up to you)
  --help                    Show this message and exit.
````

#### Download up to 1000 images searched with pattern 'ak47 shooting' 
```sh
python3 main.py download -n 1000 --pattern 'ak47 shooting'
```

### Arrange images: from in format {}{}{}{}.png
```sh
$ python3 main.py arrange --help
Usage: main.py arrange [OPTIONS]

Options:
  -p, --path TEXT   Path to source dataset
  -d, --dpath TEXT  New path for arranged images
  --help            Show this message and exit

```

#### Arrange all images in path and save to dpath
```sh
$ python3 main.py arrange --path=img_only/ --dpath=pistols/
```

### Augment images 
```sh
$ python3 main.py aug --help
Usage: main.py aug [OPTIONS]

Options:
  -p, --path TEXT    Path to resized images
  -n, --newdir TEXT  Path to resized images
  --help             Show this message and exit
```
