<% include('views/header.tpl', title='Admin', path='', role=role) %>
    <main role="main" class="container">
      <div class="jumbotron">
        <h1>Admin Functions</h1>
        <!--<p class="lead">Admin actions:</p>-->
        <ul>
            <li><a href="/admin/assignment.html">List proposals by PC member</a></li>
            <li><a href="/admin/assignCards.html">Assign papers to PC members</a></li>
        </ul>    
      </div>
    </main>
<% include('views/footer.tpl') %>

