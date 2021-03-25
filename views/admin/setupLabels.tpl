<% include('views/header.tpl', title='Setup Proposal Types', path='../', role=role) %>
    
    <main role="main" class="container">
      <div class="jumbotron">
        <h1>Setup Proposal Types</h1>
        <p class="lead">Proposal types are stored as Trello labels to make it easier to query on proposal type. To allow the Google form to map the submissions to the correct label all of the types must be create before the google form is linked up with Trello.</p>

        <%
            flaggedPresent=False
            for label in data: 
                if label['name'] == "Flagged":
                    flaggedPresent=True
                    data.remove(label)
                    break
                 end
             end
        %>
        <% if not flaggedPresent: %>
            <div class="alert alert-warning" role="alert">
                <h5>Missing Flagged Label</h5>
                This is required for flagging presentations  
                <div>
                    <form action="add_label" method="post">
                        <input type="hidden" name="name" value="Flagged"/>
                        <input type="hidden" name="color" value="red"/>
                        <input type="submit" class="btn btn-dark" name="add" value="Create now?"/>
                    </form>
                </div>   
            </div>
        <% end %>

        <h2>Submission Types</h2>
        <ul>
            <%
              found=False
              for label in data: %>
                <% if label['name']: %>
                    <!-- need to set colour of li depending on label -->
                    <li>{{ label['name'] }} (id: {{label['id']}})</li>    
                <% found= True
                    end %>
            <% end 
              if not found:
            %>
                <li>No types found</li>
            <% end %>
         </ul>
         <div id="add_type">
             <h4>Add</h4>
             <form class="form-inline" action="add_label" method="post">
                  <div class="form-group">
                    <label for="name" style="padding-right: 10px;">Submission Type:</label>
                    <input type="text" class="form-control" id="name" name="name" aria-describedby="nameHelp" placeholder="">
                  </div>
                  <div class="form-group">
                    <!-- need to update select when colour changes TODO -->
                    <select id="color" name="color" class="form-control">
                        <option style="background:#61bd4f" value="green"></option>
                        <option style="background:#f2d600" value="yellow"></option>
                        <option style="background:#ff9f1a" value="orange"></option>
                        <option style="background:#c377e0" value="purple"></option>
                        <option style="background:#0079bf" value="blue"></option>
                        <option style="background:#51e898" value="light green"></option>
                        <option style="background:#00c2e0" value="turquoise"></option>
                        <option style="background:#ff78cb" value="pink"></option>
                        <option style="background:#344563" value="black"></option>
                    </select>
                  </div>
                  <div class="form-group">
                      <input id="add" type="submit" class="btn btn-dark" name="add" value="Add"/>
                  </div>
              </form>
          </div>
      </div>
    </main>
    
<% include('views/footer.tpl') %>

