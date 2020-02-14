// Static variables that need changing for each form:
formId=''
trello_key = 'key=&token='
listId = ''; // inbox list id from https://api.trello.com/1/boards/5e45bec960c5af7dbe375164/lists

// Load all responses in trello
function loadAll() {

  //var triggers = ScriptApp.getProjectTriggers();
  var form = FormApp.openById(formId);
  var formResponses = form.getResponses();
  for (var i = 0; i < formResponses.length; i++) {
    var formResponse = formResponses[i].getItemResponses();
    var paper = responseToObject(i + 1, formResponse);
    createTrelloCard(paper)
    Logger.log('Successful creation of new submitToTrello trigger.');
  }
}

// Useful for testing
function loadLast() {
  createTrelloCardFromLatest(null);
}

// Fire off this function in the script editor to enable.
function registerTrigger() {

  var triggers = ScriptApp.getProjectTriggers();
  var form = FormApp.openById(formId);
  
  // Delete all triggers before making a brand new one.
  for(var i in triggers) {
    ScriptApp.deleteTrigger(triggers[i]);
  }
  
  // Set up a new trigger
  ScriptApp.newTrigger('createTrelloCardFromLatest')
           .forForm(form)
           .onFormSubmit()
           .create();
  
  Logger.log('Successful creation of new submitToTrello trigger.');
  
}

function createTrelloCardFromLatest(e) {
   var form = FormApp.openById(formId);
   var formResponse = form.getResponses().pop().getItemResponses();
   var paper = responseToObject(form.getResponses().length, formResponse);
   createTrelloCard(paper)
}

// This sample sends POST payload data in the style of an HTML form, including
 // a file.

function createTrelloCard(paper) {

   var payload = createCard(paper)
   // Because payload is a JavaScript object, it will be interpreted as
   // an HTML form. (We do not need to specify contentType; it will
   // automatically default to either 'application/x-www-form-urlencoded'
   // or 'multipart/form-data')
   var url = 'https://api.trello.com/1/cards?' + trello_key //optional... -&cards=open&lists=open'-
   var options = {"method" : "post",
                  "payload" : payload};

   var response = UrlFetchApp.fetch(url, options);
   var data = JSON.parse(response.getContentText());

   // add Abstract as an attachment
   var abstractBlob = Utilities.newBlob(paper['abstract']);
   payload = {
     "name":"Abstract.txt",
     "file":abstractBlob,
     "mimeType": "text/plain"
   };
   url = 'https://api.trello.com/1/cards/' + data['id'] + '/attachments?' + trello_key
   var options = {"method" : "post",
                  "payload" : payload};

   response = UrlFetchApp.fetch(url, options);
 }

function responseToObject(id, response) {
  var paper = {};
  paper['id'] = id;
  
  var index = 0;
  var contacts = [];
  var contact = {};
  // May need to edit this if questions change
  contact['name'] = response[index++].getResponse();
  contact['email'] = response[index++].getResponse();
  contacts.push(contact);
  paper['contacts'] = contacts;
  
  paper['title'] = response[index++].getResponse();
  paper['keywords'] = response[index++].getResponse();
  paper['type'] = response[index++].getResponse();
  paper['abstract'] = response[index++].getResponse();
  paper['topics'] = response[index++].getResponse(); // This is a list?
  paper['comments'] = response[index++].getResponse();
  
  var authors = [];
  for (var i = 0; i < 5 && index < response.length; i++) {
    var author = {};
    var authorResponse = response[index++]
    if (authorResponse.getItem().getTitle() == 'Name') {
      author['name'] = authorResponse.getResponse();
      author['Country'] = response[index++].getResponse();
      author['Organisation'] = response[index++].getResponse();
      author['Webpage'] = response[index++].getResponse();
      authors.push(author);
    } else {
      // run out of authors time to skip onto contacts
      break;
    }
    index++ // skip add another author question
  }
  paper['authors'] = authors;
  //var data = JSON.stringify(paper)
  //Logger.log(data);
  return paper;
}  

function createCard(paper) {  
  var title = paper['id'] + '. ' + paper['title'] + ' by ';
  
  var authors = paper['authors'];
  for (var i = 0;i < authors.length; i++) {
    title += authors[i]['name'];
    if (i == authors.length - 2) {
      title += ' and ';
    } else if (i == authors.length -1) { 
      // don't add a comma 
    } else {
      title += ', ';
    }
  }
  
  var emailList = ''
  var emails = ''
  var contacts = paper['contacts'];
  for (var i = 0; i < contacts.length; i++) {
    emailList += ' - ' + contacts[i]['name'] + ', ' + contacts[i]['email'] + '\n';
    emails += contacts[i]['email'];
    if (i != contacts.length - 1) {
      emails += ', '
    }
  }
  var desc = '**Contact**\n';
  desc += emailList;
  
  desc += '\n**Authors**\n'
  for (var i = 0;i < authors.length; i++) {
    var name = authors[i]['name'];
    var org = authors[i]['Organisation'];
    var country = authors[i]['Country'];
    var webpage = authors[i]['Webpage'];
    
    if (webpage) {
      desc += '- [';
    } else {
      desc += '- ';
    }
    desc += name;
    if (org) {
      desc += ', ' + org;
    }
    if (country) {
      desc += ', ' + country;
    }
    if (webpage) {
      desc += '](' + webpage + ')';
    }
    desc += '\n';
  }
  desc += '\n**Comments**\n'  + paper['comments'] + '\n';
  
  desc += '\n**Topics**\n'
  for (var i = 0; i < paper['topics'].length; i++) {
    desc += '- ' + paper['topics'][i] + '\n';
  }
  
  desc += '\n**Keywords:** '  + paper['keywords'] + '\n';
  
  desc += '\n**Abstract:**\n'  + paper['abstract'] + '\n';
  
  // Need to edit this for each trello board and question
  if (paper['type'] == 'Up to a ½ day workshop (4 hours)') {
    label = '5e45bec9af988c41f2dafb85';
  } else if (paper['type'] == '7 to 10 minute lightning talks') {
    label = '5e45bec9af988c41f2dafb86';
  } else if (paper['type'] == '15-20 minute presentations (plus 5-10 mins questions)') {
    label = '5e45bec9af988c41f2dafb88';
  } else if (paper['type'] == '90 minute open block (Could be panel session or grouped presentations)') {
    label = '5e45becaaf988c41f2dafb8d';
  }
   
    
 
   //POST [/1/cards], Required permissions: write
   var payload = {"name":title, //(required) Valid Values: a string with a length from 1 to 16384
                  "desc":desc, //(optional)Valid Values: a string with a length from 0 to 16384
                  "pos":"top", //(optional) Default: bottom Valid Values: A position. top, bottom, or a positive number.
                  "due": "", //(required) Valid Values: A date, or null
                  "idList":listId, //(required)Valid Values: id of the list that the card should be added to
                  'idLabels': label,
                 };
  return payload;
}
