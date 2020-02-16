% from model import cards

<% include('views/header.tpl', title='Submissions asssigned to user', path='../', role=role) %>

    <main role="main" class="container">
      <div class="jumbotron">
        <h1>Assign Papers</h1>
        <p class="lead"></p>
        <h2>Users</h2>
        <ul id="unassigned" ></ul>
        <ul id="users"></ul>
        <h2>Papers</h2>

        <table id="papers-table" class="table table-striped">
            <thead class="">
                <th scope="col">
                    Submission
                </th>   
                <th scope="col">
                    Type
                </th>   
                <th scope="col" colspan="2">
                    Assign
                </th>   
            </thead>
            <tbody id='tbody'></tbody>
        </table>
      </div>
    </main>

    <script>
        var users = {};
        var cards = [];
        var currentUser = 'Unassigned';
            
        fetch('/admin/users.json')
            .then((response) => { return response.json(); })
            .then((userJson) => {
                users = userJson;
                fetch('/admin/cards.json')
                    .then((response) => { return response.json(); })
                    .then((cardJson) => {
                    cards = cardJson;
                    for (var user in users) {
                        if (!(users[user].fullName in cards)) {
                            cards[users[user].fullName] = [];
                        }
                    }
                    populateUserCounts();
                    populatePapers();
                });
            });

        function populatePapers() {
            var table = document.getElementById("tbody")
            // Remove existing and add
            var child = null;
            for (var i = table.childNodes.length - 1; i >= 0; i--) {
                table.removeChild(table.childNodes[i]); 
            }
            var sortedNames = Object.keys(cards).sort()
            for (var i = 0; i < cards[currentUser].length; i++) {
                var card = cards[currentUser][i];

                var tr = document.createElement("tr");
    
                tr.innerHTML = '<td>' + card['name'] + '</td>';
                var type = '<td>';
                for (var j = 0; j < card.labels.length; j++) {
                    var label = card.labels[j].name
                    type += label + ", ";
                }
                type = type.substring(0, type.length - 2);
                type += '</td>';
                tr.innerHTML += type;
                tr.innerHTML += '<td><select id="select_' + card['id'] + '">'
                tr.innerHTML += '</select></td>';
                var select = tr.childNodes[2].childNodes[0];
                for (var j = 0; j < sortedNames.length; j++) {
                    var name = sortedNames[j];
                    var selected = '';
                    if (name === currentUser) {
                        selected = 'selected ';
                    }
                    select.innerHTML += '<option ' + selected + 'value="' + name + '">' + name + '</option>';
                }

                tr.innerHTML += '<td><a class="btn btn-primary" role="button" onclick="return assign(\'select_' + card['id'] + '\', \'' + card['id'] + '\');">Assign</a></td>';
                table.appendChild(tr);
            }
        }

        function assign(select_id, card_id) {
            // Get User
            userName =  document.getElementById(select_id).value;
            user_id = getUserId(userName);

            body = { 
                "user_id": user_id, 
                "card_id": card_id 
            };
            // Submit to save with card_id and user_id
            fetch('/admin/assignCard', {
                method: 'POST', 
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
              });

            // Move card from one array to another
            var card = null;    
            var index = -1;
            for (var i = 0; i < cards[currentUser].length; i++) {
                var card = cards[currentUser][i];

                if (card.id === card_id) {
                    index = i;
                    break;       
                }
            }
            cards[currentUser].splice(index,1);
            cards[userName].push(card);

            populateUserCounts();
            populatePapers();
            return false;
        }

        function getUserId(name) {
            user_id = null;
            for (var userKey in users) {
                var user = users[userKey];
                if (user.fullName === name) {
                    user_id = user.id;
                    break;
                }
            }
            return user_id;
        }

        function populateUserCounts() {
            var ul = document.getElementById("unassigned");
            emptUL(ul);
            addli(ul, 'Unassigned');

            ul = document.getElementById("users");
            emptUL(ul);
            var sortedNames = Object.keys(cards).sort()
            for (var i = 0; i < sortedNames.length; i++) {
                user = sortedNames[i]
                if (!(user === 'Unassigned')) {
                    addli(ul, user);
                }    
            }
        }

        function showUser(user) {
            currentUser = user;
            populateUserCounts();
            populatePapers();

            return false;
        }

        function addli(ul, user) {
            var li = document.createElement("li");
            var boldS = '';
            var boldE = '';
            if (user === currentUser) {
                boldS = '<b>';
                boldE = '</b>';
            }
            li.innerHTML = "<a href='#' onclick='return showUser(\"" + user + "\")'>" + boldS + user + ": " + cards[user].length + boldE + "</a>";
            ul.appendChild(li);
        }

        function emptUL(ul) {
            // Remove existing and add
            var child = ul.lastElementChild;  
            while (child) { 
                ul.removeChild(child); 
                child = ul.lastElementChild; 
            }
        }
    </script>
<% include('views/footer.tpl') %>
