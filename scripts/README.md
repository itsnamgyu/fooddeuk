# Deploy on Apache using WSGI (Ubuntu 16.04, 18.04)

## Quick start

### Install requirements

- Apache 2
- Python 3.5+

```
sudo apt install apache2
sudo apt install apache2-dev
```

### Run script!

```bash
# start at root folder
source venv/bin/activate # enable virtual environment
export PROJECT_DIR=`pwd`
./scripts/deploy_apache --host=mysite.com
```

#### Start apache service

Make sure to restart Apache service using

```bash
sudo apachectl restart
```

_May return error status if Apache is already running_
