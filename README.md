# Practical Question 2 back-end using Python

## Steps to serve this project
## Step 1 - Create venv folder
Linux
```bash
cd q2-python-backend
python3 -m venv venv
```
Windows
```bash
cd q2-python-backend
py -3 -m venv venv
```

## Step 2 - Activate the environment
Linux
```bash
. venv/bin/activate
```
Windows
```
venv\Scripts\activate
```

## Step 3 - Install all the required python library
```bash
pip install -r requirements.txt
```

## Step 4 - Configure the .env file
```
copy .env.example to .env 
change the value in your .env file
```

## Step 5 - Setup database
run command below to setup database
```
python setup_database.py
```

## Step 6 - Serve the project
```bash
python /api/api.py
```