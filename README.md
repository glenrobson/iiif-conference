# iiif-conference
Conference Submission review system using trello as a backend. This is currently tied to the 2019 IIIF Conference setup but potentially could be made more generic. 

## Submission
Submissions are entered using a Google form and a google script converts these submissions into Trello cards, adding them to an `Inbox` list. An example google form is in [Form2Trello.gs](google_scripts/Form2Trello.gs). Changes that need to be made for every form are:

 1. ```formId``` - This can be found in the URL to the google form
 2. ```trello_key``` - Private key and token for trello API
 3. ```listId``` - The id of the `inbox` list on your trello board. Can be found at https://api.trello.com/1/boards/5e45bec960c5af7dbe375164/lists
 4. Line 91: depending on the order of your questions you may need to change the way the paper object is built
 5. Line 190: Converting submission type to labels. You need to map the submission types in the form to trello label ids which you can get from: https://api.trello.com/1/boards/5e45bec960c5af7dbe375164/labels

## Trello setup
All Program Committee members need to be members of the trello board so they can review submissions. The trello board has the following lists:

 * Inbox - where submissions initially arise. 
 * Strong Accept
 * Accept
 * Weak Accept
 * Borderline Paper
 * Weak Reject
 * Reject

This system allows Program Committee members to review the submissions assigned to them and select a review category from the list above.

## Running
This project can be run either by running the python files or running the following docker script:

```./runDocker.sh```

before running both the docker script or the index script you need to add your trello keys to your enviroment. You can do this by creating a file like the following:

```
cat .apikeys 
export trello_key="trello_key"
export trello_token="trello_token"
export submission_config=conf/boston.json
```

The `runDocker.sh` script will look locally for the `.apikeys` before running the docker script.

## Running with python

Step 1: Install requirements.txt dependencies
```pip install  -r requirements.txt```

Step 2: Load trello keys to enviroment:
```source ./apikeys # see above for format of this file```

Step 3: Create users from Trello:
```./model/users.py```

Step 4: Run web service:
```./index.py```



