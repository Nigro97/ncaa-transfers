# MSiA423 Project Repository

## Nicholas Nigro

### QA: Saleel Huprikar


<!-- toc -->

- [Project charter](#project-charter)
  * [Background](#background)
  * [Vision](#vision)
  * [Mission](#mission)
  * [Success criteria](#success-criteria)
  * [Evaluation of results](#evaluation-of-results)
- [Directory structure](#directory-structure)
- [Running the app in Docker](#running-the-app-in-docker)
  * [0. Environment variables setup](#0-environment-variables-setup)
  * [1. Build the image](#1-build-the-image)
  * [2. Download the data from the API and upload it to a S3 bucket](#2-download-the-data-from-the-API-and-upload-it-to-a-S3-bucket)
  * [3. Initialize the database](#3-initialize-the-database)
    + [Create the database](#create-the-database)
    + [Defining your engine string](#defining-your-engine-string)
    + [Using environment variables to automatically generate the engine string](#using-environment-variables-to-automatically-generate-the-engine-string)
    + [Explicitly defining a local SQLite database](#Explicitly-defining-a-local-SQLite-database)
  * [4. Run K-means clustering](#4-run-k-means-clustering)
  * [5. Populate database with cleaned data](#5-populate-database-with-cleaned-data)
- [Running the reproducible model pipeline and database population in one command](#running-the-reproducible-model-pipeline-and-database-population-in-one-command)
  * [Alternative model pipeline docker run commands](#alternative-model-pipeline-docker-run-commands)
- [Running the app locally](#running-the-app-locally)
  * [Alternative local app creation docker run commands](#alternative-local-app-creation-docker-run-commands)
- [Using the NCAA Transfers app](#using-the-ncaa-transfers-app)
- [Testing](#testing)

<!-- tocstop -->
## Project Charter

### Background
Prior to 2021, the National Collegiate Athletic Association (NCAA) did not allow student-athletes in basketball, football, baseball, and hockey to transfer to new schools during their college careers without sitting out a full calendar year from playing sports as a penalty. In 2021, the NCAA passed a new rule to allow college athletes to transfer to a new school one time during college and not have to sit out the following year. This progressive and favorable move was not completed without issues though, as the impact of the new rule was first felt at the conclusion of the college basketball season in early April 2021, when basketball players could choose to transfer to a new school for the following season. The result was over 1200 players indicating they were looking to transfer within a week of the seasons' conclusion and a projected 2000 total in the following weeks. This shattered the records of the number of potential transfers in one offseason by at least doubling the prior record of 700 transfers and potentially tripling it. Basketball coaches were sent scrambling to quickly evaluate thousands of available players to recruit to their team before the players made their final new-team decisions, which would happen in only a matter of days or weeks.

### Vision
With the help of my app, basketball coaches could evaluate players quickly to find those that would fit into missing holes on their roster or match the skills they typically want for players on their team. Speed is critical during this overwhelming transfer period in order to show interest in a player and recruit them before they commit to a different team. This app is designed to connect teams and players together to allow players to evaluate all team interest they should receive and find the best possible fit for their future playing careers without letting any opportunities slip through the cracks.

### Mission
The app groups players into specific player types using a clustering algorithm. Traditional player types such as guard, forward, and center are broadly defined and outdated, so these new player groupings should give more accurate insights into how a player plays the game of basketball. The player types will be based off of a player's in game statistics from the prior season such as points, rebounds, assists, etc. per game. The app's direct users will consist of college basketball coaches. Coaches can enter a desired player type and get suggested matches on players with similar statistics that they can target to recruit.

Data will be obtained from sports-reference.com through its player season finder to collect statistics on college basketball players from the 2020-2021 season. Statistics on over 200 players (2000 rows) will be used. Data is available through the sportsipy python package that uses the API for sports-reference.com.

### Success criteria
For the clustering algorithm, several metrics will be used to evaluate the clustering performance. The within-cluster SSE and Silhouette score will be used to evaluate the cluster solutions. Different clustering types, numbers of clusters, and combinations of features will be tried to find a maximum spike in Silhouette scores and elbow in the within-cluster SSE plot, but an exact success threshold cannot be estimated at this time without context. A directly measurable form of success is to fit the clusters on two different random seeds and then find the cluster assignments for each. Over 80% of the observations should be assigned to the same cluster for both cluster fittings in order to show the clusters are stable. The final number of clusters should properly fit the situation, as there should be between roughly 4-10 different player types in order to get several categories of players. Another specific goal is that each cluster should be able to be labeled with a different short description of the player type encapsulated by that cluster which will show that each cluster has an interpretable trend and is distinct.

To evaluate the business success of the app, when the app is deployed at least 10% of the player recommendations given to a coach user should lead to mutual interest between the specific player and team. Mutual interest will be defined as a connection or conversation that occurs between the player and team where both parties leave the door open at the end of the conversation for a potential transfer of that player to that school occuring during the subsequent transfer recruiting process. This mutual interest data would be provided by the player or team directly from those who used the app.

### Evaluation of results
K-means clustering was ultimately chosen as the best clustering algorithm for this purpose. The equal cluster sizes provided by this algorithm made most sense for this use case. Five clusters were chosen to create five new player types. The number of clusters vs. within-cluster SSE and Silhouette score plots can be seen in the models folder to show the exploratory process of choosing an optimal number of clusters. There is also a plot of points per minute vs. 3-point attempt rate that shows the separation of clusters across those two dimensions. Five clusters was roughly the elbow of the within-cluster SSE plot and since there was no spike in the Silhouette score plot, there was no obvious indication of the best number of clusters. Five clusters makes sense for basketball since there are five players on the court at one time, and each player usually has a different role. The clusters were also able to be descriptively labeled when using five clusters, while using six or more clusters there seemed to be more overlap between the clusters which made it tougher to define each as a player type. The clusters were also found to be stable, since two clustering runs with different random seeds resulted in 92.67% of observations being classified into the same cluster in each run, meeting the success criteria threshold of 80%.

The five new player types that were generated as a result of clustering are as follows:

Volume Shooter and Scorer: Smaller or average sized players that shoot and score many points
O and D Ball Handler: Smaller players that focus on assists and steals instead of shooting
Three-Point Specialist: Smaller or average sized players that shoot more 3 pointers than 2 pointers
Shooting Big: Tall players that can shoot 3 pointers
Paint Presence: Tall players that do not shoot 3 pointers and focus on great defense

## Directory structure 

```
├── README.md                         <- You are here
├── app
│
├── config                            <- Directory for configuration files 
│   ├── logging/                    <- Configuration of python loggers
│   ├── config.yaml                 <- Yaml file for Python scripts
│   ├── flaskconfig.py              <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated.
│   ├── external/                   <- External data sources, raw data from API
│
├── deliverables/                     <- Contains project presentation
│
├── models/                           <- Trained model predictions and/or model evaluation
│
├── src/                              <- Source python modules for the project 
│
├── test/                             <- Files necessary for running model tests 
│
├── Dockerfile                        <- Dockerfile for building image to run Python modules separately
├── Dockerfile_model                  <- Dockerfile for building image to run model pipeline 
├── Dockerfile_app                    <- Dockerfile for building image to run app 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── app.py                            <- Python module that runs the app
├── requirements.txt                  <- Python package dependencies 
├── requirements_app.txt              <- Python package dependencies for app
├── run-pipeline.sh                   <- Bash script used to streamline entire model pipeline
├── run-tests.sh                      <- Bash script that runs the unit tests
```

## Running the steps separately for the app in Docker

### 0. Environment variables setup

The environment variables that are necessary for connecting to S3 can be set through the following commands:

```bash
export AWS_ACCESS_KEY_ID=<aws_access_key_id>
export AWS_SECRET_ACCESS_KEY=<aws_secret_access_key>
export AWS_DEFAULT_REGION=<aws_region>
```
us-east-2 is the default region for my S3 bucket and RDS database

The environment variables used to connect to the RDS database can be set through the following commands:

```bash
export MYSQL_USER=<mysql_username>
export MYSQL_PASSWORD=<mysql_password>
export MYSQL_HOST=<mysql_host>
export MYSQL_PORT=<mysql_port>
export DATABASE_NAME=<database_name>
```

Alternatively, the entire SQL Alchemy URI could be provided as an environment variable instead of the five separate exports above:

```bash
export SQLALCHEMY_DATABASE_URI=<sqlalchemy database uri>
```

The SQLALCHEMY_DATABASE_URI is defined by a string in following format:

`mysql+pymysql://<mysql_username>:<mysql_password>@<mysql_host>:<mysql_port>/<database_name>`

Please also note if you are connecting to RDS that you need to be on the Northwestern VPN prior to executing the commands later on.

### 1. Build the image 

To build the Docker image, run from this directory (the root of the repo): 

```bash
 docker build -f Dockerfile -t ncaa_transfers .
```

This command builds the Docker image, with the tag `ncaa_transfers`, based on the instructions in `Dockerfile` and the files existing in this directory.

### 2. Download the data from the API and upload it to a S3 bucket

The dataset can be downloaded from sports-reference.com through the sportsipy library available in Python. 
WARNING: It can take up to 20 minutes to download the full dataset from the API. It is only 4 MB, but it takes a long time to pull fully due to restraints from the API on the rate data can be pulled.

To download the data through the sports-reference API and upload it to an S3 bucket run:

```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION ncaa_transfers python3 run.py get_data --savepath=<bucket_path> --source=api
```

To download the data through the sports-reference API and download it to a local path run the same command but replace the path argument to denote a local path. By default, the saved data location is `data/external/sports_ref.csv` :

```bash
docker run ncaa_transfers python3 run.py get_data --savepath=<local_path> --source=api
```

To upload data currently stored in the `data/external` folder to an S3 bucket run:

```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION ncaa_transfers python3 run.py get_data --savepath=<bucket_path> --source=local
```

In general, the `savepath` argument corresponds to the location to save the data (either S3 bucket path or local path). The `source` argument is set to either the `local` keyword to load the data from the local file location `data/external/sports_ref.csv` or instead the `api` keyword to download the data from the API.

To summarize the above commands and add more context, the two commands below are explicit examples of what I run to download data from the API and then upload to my S3 bucket in two separate steps. Simply replace my bucket path with your bucket path below to get the data from the API to your bucket. I would recommend doing the data download from the API and then upload to S3 in two separate steps as shown because the slowness of the connection to the API I believe can be hindered by the connection to the S3 bucket which increases the chances of a Timeout or Connection Error:

```bash
docker run ncaa_transfers python3 run.py get_data --savepath=data/external/sports_ref.csv --source=api

docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY ncaa_transfers python3 run.py get_data --savepath=s3://2021-msia423-nigro-nicholas/raw/sports_ref.csv --source=local
```

One final note, there appears to sometimes be issues with uploading data to the root of an S3 bucket. I would recommend uploading to a specific folder within the S3 bucket such as "raw" as shown in the example above to avoid these issues.

### 3. Initialize the database 

#### Create the database 
To create the database in AWS RDS or SQLite run: 

```bash
docker run ncaa_transfers python3 run.py create_db --engine_string=<engine_string>
```

By default, this command creates a database at `sqlite:///data/results.db`. You can replace the engine string with a custom SQLite path or RDS path if desired. 

#### Defining your engine string 
A SQLAlchemy database connection is defined by a string containing variables with the following format:

`mysql+pymysql://<mysql_username>:<mysql_password>@<mysql_host>:<mysql_port>/<database_name>`

The engine string can be typed directly and fully as the `<engine_string>` argument, or can be generated in the correct format using environment variables as explained below.

#### Using environment variables to automatically generate the engine string

Run the following command with no engine string argument to auto-generate the engine string based off of the environment variables.

```bash
docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_HOST -e MYSQL_PORT -e DATABASE_NAME ncaa_transfers python3 run.py create_db
```

Alternatively, the entire SQL Alchemy URI could be exported as an environment variable instead and then the following command can achieve the same result to upload data to the RDS database:

```bash
docker run -e SQLALCHEMY_DATABASE_URI ncaa_transfers python3 run.py create_db
```

If environment variables are not exported first as show in the environment variables section (0), then the default engine string of `sqlite:///data/results.db` will be used.

##### Explicitly defining a local SQLite database 

A local SQLite database can be created for development and local testing. It does not require a username or password and replaces the engine string with the path to the database file: 

```bash
docker run ncaa_transfers python3 run.py create_db --engine_string=<sqlite_database_path>
```

### 4. Run K-means clustering

To pull the raw data from S3, lightly clean it, and run K-means clustering in one step, the following command can be run. The S3 path to my S3 bucket is: s3://2021-msia423-nigro-nicholas/raw/sports_ref.csv

```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION ncaa_transfers python3 run.py get_clusters --loadpath=<S3_data_path> --savepath=<cleaned_data_path_to_save_to>
```

To pull data from a local path instead, the command can be modified as follows:

```bash
docker run ncaa_transfers python3 run.py get_clusters --loadpath=<local_raw_data_path> --savepath=<cleaned_data_path_to_save_to>
```
The default path for the loadpath argument is data/external/sports_ref.csv while the default path for the savepath is data/sports_ref_clean.csv. The data being saved to the savepath is the cleaned dataframe with a new column containing the cluster labels.

### 5. Populate database with cleaned data

To upload data to a RDS database, run the following command:

```bash
docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_HOST -e MYSQL_PORT -e DATABASE_NAME ncaa_transfers python3 run.py populate_db --engine_string=<engine_string> --loadpath=<cleaned_data_loadpath>
```

Just like before, the SQLALCHEMY_DATABASE_URI environment variable can be used for the engine string instead if it is explicitly exported:

```bash
docker run -e SQLALCHEMY_DATABASE_URI ncaa_transfers python3 run.py populate_db --engine_string=<engine_string> --loadpath=<cleaned_data_loadpath>
```

The default value for the engine_string argument is a local database at sqlite:///data/results.db and the default loadpath argument is data/sports_ref_clean.csv.

A database can also be created at a different local path through a modification to the command to explicitly set the local database path:

```bash
docker run ncaa_transfers python3 run.py populate_db --engine_string=<local_database_path> --loadpath=<cleaned_data_loadpath>
```

## Running the reproducible model pipeline and database population in one command

The following two commands will build the docker image and then run the docker command to run the full model pipeline starting from downloading the raw data from the S3 bucket until uploading the cleaned data with the cluster labels attached to a newly created RDS database. Make sure to export the environment variables as shown in step 0 of the previous section above. The S3 bucket storing the data is s3://2021-msia423-nigro-nicholas/raw/sports_ref.csv and the data will automatically pulled from there with these docker commands, but the database will be created entirely from scratch using the enviornment variables specified.

Build docker image:
```bash
docker build -f Dockerfile_model -t ncaa_model .
```

Run full model pipeline from S3 to database population:

```bash
docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_HOST -e MYSQL_PORT -e DATABASE_NAME -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION --mount type=bind,source="$(pwd)",target=/app/ ncaa_model run-pipeline.sh
```

The artifacts generated from the model pipeline step include three plots, a percent similarity metric, the cleaned data with cluster labels attached in csv form, and a populated database. The plots are a number of clusters vs. within-cluster SSE plot, a number of clusters vs. Silhouette score plot, and a plot that visualizes the cluster separation across two dimensions. The percent similarity metric is the percent of cluster assignments that were the same for two clustering fits with different random seeds. This metric shows the stability of the clusters. 

### Alternative model pipeline docker run commands

The following command will make the database locally at sqlite:///data/results.db instead of RDS:

```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION --mount type=bind,source="$(pwd)",target=/app/ ncaa_model run-pipeline.sh
```

The following command will make the database using the SQLALCHEMY_DATABASE_URI explicitly if it was exported:

```bash
docker run -e SQLALCHEMY_DATABASE_URI -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION --mount type=bind,source="$(pwd)",target=/app/ ncaa_model run-pipeline.sh
```

## Running the app locally

The following two commands will build the docker image to run the app locally and then a docker run command to run the app. The RDS database will be queried during app usage in order to retrieve the correct data to display based on user inputs. To see the app, navigate to 

```bash
docker build -f Dockerfile_app -t ncaa_app .

docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_HOST -e MYSQL_PORT -e DATABASE_NAME -p 5000:5000 ncaa_app python3 app.py
```

The app should now be accessible through http://localhost:5000 in the browser.

Once again, be sure to export necessary environment variables and connect to the Northwestern VPN as shown previously before executing the docker run command. 

### Alternative local app creation docker run commands

The following command will pull data from a local database at sqlite:///data/results.db instead of RDS:

```bash
docker run -p 5000:5000 ncaa_app python3 app.py
```

The following command will access the database using the SQLALCHEMY_DATABASE_URI explicitly if it was exported:

```bash
docker run -e SQLALCHEMY_DATABASE_URI -p 5000:5000 ncaa_app python3 app.py
```

## Using the NCAA Transfers app

The app can be accessed through this link while connected to the Northwestern VPN: http://ncaa-Publi-1WJOM0Y6XHMJM-2056926913.us-east-2.elb.amazonaws.com

Two user inputs are required. The first is to select a player type from the dropdown menu. These player types are the cluster labels for the various clusters generated by K-means clustering. They are descriptive labels of the type of players in each cluster. These labels given much more information than the outdated and very general player positions of point guard, small forward, etc. All players in the database will be filtered by the selected player type. Then, the second user input is the sort column. The sort column will sort the filtered players in descending order based on the specified column. The top 100 players matching the player type and sorting based on the sort column statistic will find and display the top players in a certain statistic for the selected player type. This would allow coaches using the app to locate high performing players that fit the needed skills for their team. A coach may notice they have no tall players that can play defense against other tall players but also can produce offense through shooting. Therefore, the coach could selected 'Shooting Big' as the player type for the first input. Then, maybe the coach prioritizes ball passing by his/her taller players, so he/she chooses 'Assists per Minute' from the dropdown for the second input of the sort column. Now, when pressing submit, the top 'Shooting Big' players that can pass the ball best. After seeing the top names, now the coach could reach out to the players offline and try to recruit them to join his/her team for the next season. This generates more opportunities for the players to be found by coaches and be able to fit into a team where they can produce at the highest level possible.

## Testing

To run unit tests for the data cleaning and featurization functions, build the Docker image for the full model pipeline if you have not done so already:

```bash
docker build -f Dockerfile_model -t ncaa_model .
```

Then, the following Docker run command will run all tests to ensure they pass:

```bash
docker run ncaa_model run-tests.sh
```
