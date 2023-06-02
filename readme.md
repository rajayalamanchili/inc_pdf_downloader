## Environment setup Instructions
***

`python3 -m venv env`

`source env/bin/activate`

`python3 -m pip install --upgrade pip`

`pip install -r requirements_dev.txt`

`playwright install`

`export PYTHONPATH=$PYTHONPATH:$(pwd)`

<br/><br/>



## Input json file format (eg: config.json)
***
```
{
    "settings": {
        "homepage_url": "https://www.safeco.com/",
        "policy_details_api": "https://customer.safeco.com/accountmanager/api/policy",
        "doc_details_api": "https://customer.safeco.com/accountmanager/api/document/policy"
    },
    "secrets": {
        "usrname": "****************",
        "pwd": "***************"
    }
}
```
<br/><br/>


## Running script
***

`python3 src/main.py config.json`
