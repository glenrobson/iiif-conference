
<table class="table table-striped">
    <thead class="">
        <th scope="col">
            Number
        </th>
        <th scope="col">
            Title
        </th>
        <th scope="col">
            Authors
        </th>   
        <th scope="col">
           Status 
        </th>   
         % if includeAction:
            <th scope="col">
                
            </th>   
          % end    
    </thead>
    % for card in cardsJson:
    <tr>
        <%
            cardName = card['name']
            number = cardName.split('.')[0]
            endPart = cardName.split('{}. '.format(number))[1]
            title = ' by '.join(endPart.split(' by ')[0:-1])
            author = endPart.split(' by ')[-1]
        %>
        <td>{{ number }}</td>
        <td>{{ title }}</td>
        <td>{{ author }}</td>
        <td><!-- get list -->
            {{ lists[card['idList']].replace('Inbox','Awaiting Review') }}
           <%
                flagged = False
                for label in card['labels']:
                    if label['name'] == 'Flagged':
                        flagged = True
                        break
                    end    
                end        
           %>
             % if flagged:        
                    -  <b>Flagged</b>
             % end  
        </td>
         % if includeAction:
            <td>
                % if lists[card['idList']] != 'Inbox':
                    <a class="btn btn-secondary" href="review/{{ card['id'] }}.html" role="button">
                        Edit Review
                    </a>
                % else:    
                    <a class="btn btn-dark" href="review/{{ card['id'] }}.html" role="button">
                        Add Review
                    </a>
                % end
            </td>
         % end    
    </tr>
    % end 
</table>

