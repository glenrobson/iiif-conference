# iiif-conference
Conference Submission review system using trello as a backend. The main part of this system is reviewing submissions but it also has helper functions to manage the process from submission to publication of the program. Configuration and setup instructions are below organised by process stage.

A lot of the configuration per conference is stored in a configuration file. See [boston.conf](conf/boston.json) for a complete example. Details of the different fields are detailed below as they are needed

## Stage 1: Submission

### Google Form
Submissions are entered using a Google form and a google script converts these submissions into Trello cards, adding them to an `Inbox` list. An example google form is in [Form2Trello.gs](google_scripts/Form2Trello.gs). Changes that need to be made for every form are:

 1. ```formId``` - This can be found in the URL to the google form
 2. ```trello_key``` - Private key and token for trello API
 3. ```listId``` - The id of the `inbox` list on your trello board. Can be found at https://api.trello.com/1/boards/5e45bec960c5af7dbe375164/lists
 4. Line 91: depending on the order of your questions you may need to change the way the paper object is built
 5. Line 190: Converting submission type to labels. You need to map the submission types in the form to trello label ids which you can get from: https://api.trello.com/1/boards/5e45bec960c5af7dbe375164/labels

### Trello setup

For the submission stage you need to create a list called `inbox` and have the following labels that match the submission type:
 * Workshop
 * Lightning talk
 * Presentation
 * Panel

You also need a label called flagged:
 * Flagged

This is used in the next stage to flag submissions that should be discussed in the Program Committee 

## Stage 2: Evaluation of submissions
### Trello setup
All Program Committee members need to be members of the trello board so they can review submissions. The trello board has to have the following lists:

 * Inbox - where submissions initially arise (Should have been created in Step 1).
 * Strong Accept
 * Accept
 * Weak Accept
 * Borderline Paper
 * Weak Reject
 * Reject

Note case and spaces are important. 

### Submissions System
This system allows Program Committee members to review the submissions assigned to them and select a review category from the list above. To deploy this system in production setup an [Amazon ECS](https://aws.amazon.com/ecs/) instance that can deploy the docker file `Dockerfile`. This will run the python web application on port 9000. The IIIF instance of this is aviliable at:

https://conference.iiif.io

and is tied to github so that changes are automatically deployed. In production remmeber to set the `trello_key`, `trello_token` and `submission_config` envoriment keys correctly.

#### Setting up the Conference config
For this stage you need a config similar to the following:
```
{
    "board_id": 
    "website": {
        "title": "IIIF Boston Conference System",
        "hero_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Ray_and_Maria_Stata_Center_%28MIT%29.JPG/2560px-Ray_and_Maria_Stata_Center_%28MIT%29.JPG"
    },
    "email_templates": {
        "account_info": "email_templates/boston/account_info.txt",
    }
}
```
stored in the conf directory. The Submission system gets access to this config by looking in the enviroment for `submission_config` and this can be defined as:

```export submission_config=conf/boston.json```

but to make development easier this can be stored in the `.apikeys` script detailed below. The config elements are:

 * `board_id`: The trello board id
 * `website/title`: The title to be used on the submissions system website
 * `website/hero_image`: The image to be used as a background on the submission system
 * `email_templates/account_info`: The text to be used to give details to the program committe on their username and password for the Submission System.

#### Running locally
This project can be run either by running the python file `index.py` or running the following docker script:

```./runDocker.sh```

before running both the docker script or the index script you need to add your trello keys to your enviroment. You can do this by creating a file like the following:

```
cat .apikeys 
export trello_key="trello_key"
export trello_token="trello_token"
export submission_config=conf/boston.json
```

The `runDocker.sh` script will look locally for the `.apikeys` before running the docker script.

#### Assigning submissions to PC members
Once you have the Submission System up and running you need to ensure your user is an Admin user. Currently this is hardcoded in the `model/users.py` file. If you are an Admin user you should see a Admin link once you log in to the Submission system. If you click this link you should see the following two options:

 * List proposals by PC member
 * Assign papers to PC members

List proposals by PC member gives an overview of the process and can be used to monitor how many submissions still need reviewing. To assign papers to PC members click on the second link. This page starts by showing you all of the unassigned submissions and allows you to select a PC memeber in the drop down and click Assign. This will update the counts at the top of the page to ensure you are distrbuting your submissions fairly. Users are picked up from the trello board so ensure they are part of the trello board. 

### PC member role
Once the PC member logs in they will see a list of submissions to review. They then click Add Review and get the option to:

 * Select the acceptance of the submission from a dropdown containg `Strong Accept`, `Accept`, `Weak Accept`, `Borderline Paper`, `Weak Reject` and `Reject`
 * In the same drop down they also have the option to select `Request re-assignemnet` which they should select if they have a conflict of interest ith the submission. 
 * They can add a comment and should add a comment if they select `Borderline Paper or below.
 * They can flag the submission for further discusion by the Program Committee. Reasons for flagging include:
   * Mistakes in the submission e.g. Title incorrect
   * Comments to PC in submission e.g. I can only present on Wednesday or I would like to present remotely.

## Stage 3: Program Committee Evaluation Discussion
Once all of the submissions have been reviewed the PC meets to discuss any submissions which are rated as `Borderline Paper` or below and any submissions which have been flagged. The meeting is conducted by sharing the Trello board and going through each of the relevant cards and adding comments. The outcome of this process should be:

 * Cards in `Strong Accept`, `Accept`, `Weak Accept` or `Borderline Paper` and that aren't flagged should be ready to go and OK to be automatically contacted to say their submission has been accepted. 
 * Any cards in `Weak Reject` and `Reject` will have to be manually contacted to say why their submission were rejected. 
 * Any cards that shouldn't be automatically contacted should be flagged. These cards will need a manual email. 

Cards that need to be handled manually should have a comment to say why.

## Stage 4: Notification of acceptance
Now all of the submissions have been reviewed we are ready to notify the authors if they have been successful. As part of this process we also want to get authors to approve their submission on the website and correct any errors that were flagged in the review. The first stage is to deploy the approved submissions to the IIIF website.

### Building the IIIF conference submissions website
This is done by converting the Trello cards into a YAML file that can be shown on the IIIF Jekyll website. To do this run the following script:

```
./scripts/generateYaml.py ../../iiif/website/source/_data/2020-conference-submissions.yml
```

This will convert all of the cards in `Strong Accept`, `Accept`, `Weak Accept`, `Borderline Paper` to a YAML file that can be added to the IIIF website. The IIIF website uses the [page_gen](https://github.com/avillafiorita/jekyll-datapage_gen) Jekyll plugin to create pages from a YAML file. This takes the following config in the `_config.yml` file:

```
  - index_files: false
    data: '2020-conference-submissions'
    template: '2020_submission'
    name: 'id'
    dir: 'event/2020/boston/program'
    extension: 'html'
```

where:
 * `data: '2020-conference-submissions'` is the name of the yaml file in `_source/data/` directory and called 2020-conference-submissions.yml
 * `template: '2020_submission'` is the template which converts the yaml file to html and is in `_source/_layouts/2020_submission.html`
 * `name: 'id'` is the Yaml field to use for naming the output file. In this case it is the submission id
 * `dir: 'event/2020/boston/program'` this is the website path for the output html. 
 * `extension: 'html'` is the extension of the output file

Once you have the page_gen files and submissions yaml in place you can create a pull request on the IIIF website repo and this will create a preview website which you can share with authors. 

### Notification of acceptance

The evaluation stage will leave cards in the lists stated above (`Strong Accept` etc) and some will be flagged for further discussion. The script:

```
./scripts/notifications.py accept_submission
```

Will email all authors of submissions in the `Strong Accept`, `Accept`, `Weak Accept` and `Borderline Paper` categories that aren't flagged that their submission has been accepted. If the email sends successfully then the cards will be moved to a `Ready to go` list. Any flagged submissions are not emailed but a copy of the email is placed in `/tmp/flagged` so that it can be used to manually email authors.

The email uses a google mail account and you will have to download a credentials.json file from google by registering for a [GMail API key](https://developers.google.com/gmail/api/quickstart/python). On first run of the notifications script you will be asked to authorise the script to send emails using your google account.  

To set the text of the message set the following property in the config under `email_templates`. You can also set the preview URL for the submission details under the website part of the config:

```
    "email_templates": {
        "account_info": "email_templates/boston/account_info.txt",
        "accept_submission": {
            "from": "events@iiif.io",
            "subject": "Submission {{ paper['id'] }}: 2020 IIIF Boston Conference",
            "text": "email_templates/boston/accept_submission.txt",
            "preview": "https://preview.iiif.io/root/boston_program/event/2020/boston/program/{}/"
        }
    }
```

The subject is the subject of the email message and the text is the text body of the email. Both use the `bottle` template format and the following details can be substituted:
 * `{{ paper['id'] }}`:  The id for the submission usually a running number starting from the first submission
 * `{{ paper['name']}}`: Name of the submissions submitter
 * `{{ paper['title'] }}`: Title of the submission
 * `{{ paper['type'] }}`: Type of submission e.g. Presentation / Lightning talk / Panel
 * `{{ paper['url'] }}`: The URL to the submission details on the preview website. This is set in the config above with `{}` which is replaced by the paper id.

The `from` part of the config is the email address that the acceptance email should come from. Ensure in Google mail you are able to send from this address.

### Rejected submissions
These will have to be manually emailed and no email will be in `/tmp/flagged`. They also won't appear on the website. Once authors have been contacted these cards can stay on the `rejected` list and won't be included on any further steps.

## Stage 5: Making corrections 
At this point it is useful to have the following lists in trello:

 * `Inbox` - retained incase there are late submissions. This is where they will appear.
 * `Questions on acceptance` - for cards where the author has been asked to update their abstract but it may still be rejected
 * `Scheduling` - for cards that are accepted but authors have asked to present on certain days
 * `Needs work` - submissions are good enough to go on the program but there is an error in the details e.g. typos etc
 * `Ready to go` - authors have been contacted and these presentations are ready to go into the program
 * `Rejected` - submissions that were rejected in the previous stage

### Making corrections
Corrections can be made by directly editing the trello cards. Progress can be monitored by moving cards between different lists and flagging ones that aren't yet finished. 

### Working with flagged submissions
For the flagged submissions created in the previous stage and there should be an email in `/tmp/flagged` for this submission. Flagged submissions will be deployed to the website so that it can be shared with authors and they can see the changes that need to be made. 

These flagged submissions will have to be contacted manually. If there are changes these can be done using Trello and once fixed cards can be moved to 'ready to go'


## Stage 6: Building the program
This work is mostly done in the [IIIF Jekyll site](https://github.com/IIIF/website) and involves grouping presentations around a theme and fitting them into the program. To help with this work there is an Admin function that will list all accepted presentations by type.

# Running locally with python

Step 1: Install requirements.txt dependencies
```pip install  -r requirements.txt```

Step 2: Load trello keys to enviroment:
```source ./apikeys # see above for format of this file```

Step 3: Create users from Trello:
```./model/users.py```

Step 4: Run web service:
```./index.py```



