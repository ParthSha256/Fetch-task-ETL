
# Fetch Rewards : ETL off a SQS Queue

This project's goal is to demonstrate a smooth data management process that involves extracting data from a SQS (Simple Queue Service) queue, transforming it, and then loading the modified data into a PostgreSQL database. A major goal is to make it easier for data analysts to identify duplicates while still protecting Personal Identifiable Information (PII) through encryption. This project intends to optimize data management, deploy sophisticated security measures, and simplify data analysis in order to efficiently safeguard sensitive information.
    
Note : Instructions are for windows


## What you will need to begin :
a) [Docker](https://docs.docker.com/engine/install/)

b) [Docker Compose](https://docs.docker.com/compose/)

c) [Python](https://www.python.org/downloads/)
                    
d) [Psql](https://www.postgresql.org/download/windows/)


## Steps to run the application:
Step 1 : Install docker and docker compose

Step 2 : On the same directory, start both the containers of yaml file.

cmd/powershell : 
```
docker compose up -d

```

Step 3 : Connect to docker's postgres database. Here, mine is fetch_task-postgres-1

cmd/powershell :
```
docker exec -tiu postgres fetch_task-postgres-1 psql

```

Enter password when prompted.


Step 4 : Setup python venv and install dependencies from requirements.txt

cmd/powershell : 
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```  

Step 5 : Run the script from current directory.

cmd/powershell : 
```
python ./main.py
```

Step 6 : You will see the data getting loaded from SQS to postgres database. In the same
cmd/powershell window where connection is established to database and you have psql terminal, type:

cmd/powershell :
```
select * from user_logins;
```

Step 7 : You should be able to see populated table in database.

Step 8 : You can shutdown the opened containers by writing following in the terminal.

```
docker compose down
```
And, session shall end.

## Trouble Shooting
Delete the table and run compose again
```
docker exec fetch_task-postgres-1 psql -U postgres -c 'drop table user_logins'
```

## Project Structure

```
./
├── main.py
├── Questions.txt
├── README.md
├── requirements.txt
└── docker-compose.yml
```