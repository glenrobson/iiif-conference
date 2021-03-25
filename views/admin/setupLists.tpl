<% include('views/header.tpl', title='Setup Proposal Types', path='../', role=role) %>
    
    <main role="main" class="container">
      <div class="jumbotron">
        <h1>Setup lists</h1>
        <p class="lead">Different stages of the process require different lists to be present. This page shows the current Trello lists and allows you to create missing ones if required</p>
        <h2>Current Lists</h2>
        <ul>
            <%
              found=False
              list_names = {}
              for list in data: %>
                <% if list['name']: %>
                    <!-- need to set colour of li depending on label -->
                    <li>{{ list['name'] }} (id: {{list['id']}})</li>    
                <% found= True
                    list_names[list['name']] = list['id']
                    end %>
            <% end 
              if not found:
            %>
                <li>No lists found</li>
            <% end %>
         </ul>

         <h2>Stages</h2>
         <h3>Stage 1: Submission</h3>
         <p>Required lists:</p>
         <ul>
            <li>
             <% if 'Inbox' in list_names: %>
                Inbox (id: {{list_names['Inbox']}})
             <% else: %>
                 
                <form action="add_list" method="post" class="form-inline">
                    <div class="form-group">
                        <label for="name" style="padding-right: 10px;">Missing list - Inbox</label>
                        <input type="hidden" name="name" value="Inbox"/>
                        <input type="submit" class="btn btn-dark" id="name" name="add" value="Create"/>
                    </div>
                </form>
             <% end %>
             </li>
         </ul>

         <h3>Stage 2: Evaluation of submissions</h3>
         <p>Required lists:</p>
         <% print (decisionList) %>
         <table class="table table-striped table-bordered ">
              <thead class="thead-dark">
                <tr>
                  <th scope="col">Id</th>
                  <th scope="col">Name</th>
                  <th scope="col">Present?</th>
                  <th scope="col">Create</th>
                </tr>
              </thead>
              <tbody>
            <% for decision in decisionList: %>
            <tr>
             <% if decision in list_names: %>
                <td>{{list_names[decision]}}</td>
                <td>{{decision}}</td>
                <td>YES</td>
                <td></td>
             <% elif decision != 'Request re-assignement': %>
                <td></td>
                <td>{{decision}}</td>
                <td>NO</td>
                <td>
                <form action="add_list" method="post" class="form-inline">
                    <div class="form-group">
                        <input type="hidden" name="name" value="{{ decision }}"/>
                        <input type="submit" class="btn btn-dark" name="add" value="Create"/>
                    </div>
                </form>
                </td>
             <% end %>
             </tr>
             <% end %>
             </tbody>
             </table>
         </ul>
      </div>
    </main>
    
<% include('views/footer.tpl') %>

