% from model import cards

<% include('views/header.tpl', title='Submissions to review', path='', role=role) %>

    <main role="main" class="container">
      <div class="jumbotron">
        <h1>Submissions to review</h1>
        <p class="lead">Click on one of ths submissions below to add your review.</p>

        <% include('views/card.tpl', cardsJson=cardsJson, user=user, includeAction=True, lists=lists) %>

      </div>
    </main>

<% include('views/footer.tpl') %>
