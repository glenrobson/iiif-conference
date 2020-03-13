<% include('views/header.tpl', title='Proposals by Type', path='../', role=role) %>
<%
    for key in data:
        print ('Key: {}'.format(key))
    end    
%>
    <main role="main" class="container">
      <div class="jumbotron">
        <h1>Proposals by Type</h1>
        <p class="lead">To help organise the program, here are the proposals organised by type i.e Workshop / Lightning talk / Presentation or Panel</p>
        <% for submissionType in cardsObj.presentationTypes: %>
            <% if submissionType in data: %>
                <h2>{{ submissionType }}</h2>

                <% include('views/card.tpl', cardsJson=data[submissionType], user=user, includeAction=False, lists=lists) %>
            <% end %>
        <% end %>

      </div>
    </main>

    <% include('views/footer.tpl') %>
