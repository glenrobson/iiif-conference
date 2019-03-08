% from model import cards

<% include('views/header.tpl', title='Submissions asssigned to user', path='', role=role) %>

    <main role="main" class="container">
      <div class="jumbotron">
        <h1>Submissions by User</h1>
        <p class="lead"></p>
        <h2>Unassigned ({{ len(data['Unassigned']) }} submissions)</h2>
        <% include('views/card.tpl', cardsJson=data['Unassigned'], user=None, includeAction=False, lists=lists) %>
        % for user in data:
            % if user != 'Unassigned':
                <h2>{{ user }} ({{ len(data[user]) }} submissions)</h2>
                <% include('views/card.tpl', cardsJson=data[user], user=None, includeAction=False, lists=lists) %>
            % end
        % end    
      </div>
    </main>

<% include('views/footer.tpl') %>
