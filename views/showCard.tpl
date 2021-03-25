<% import markdown
from model import cards

if 'review' in card:
    (reviewUser, decision, comment) = cards.decodeReview(card['review']['data']['text'])
    print ("user {} decision '{}' comment {}".format(reviewUser, decision, comment))
else:
    (reviewUser, decision, comment) = ('', '', '')
end
flagged = ''
for label in card['labels']:
    if label['name'] == 'Flagged':
        flagged = 'checked'
        break
    end
end
%>

<% include('views/header.tpl', title='Reviewing Submission', path='../', role=role) %>
    <main role="main" class="container">
      <div class="jumbotron">
        <h1>Reviewing Submission</h1>
        <p class="lead">Your are reviewing the following submission. Please note whether this submission should be accepted and add any comment for the program committee.</p>
        <div class="submissions">
             <h4>{{ card['name'] }}</h4>
            % for label in card['labels']:
                <p><b>Type: </b> {{ label['name']}}</p>
            % end    
            {{! markdown.markdown(card['desc']) }}
        </div>    
        <br/>
        <br/>
        <h3>Review</h3>
        <form action="/review/{{card['id']}}.html" method="post">
             <div class="form-group">
                <label for="decision">Grade submission on whether it should be accepted, You can also select re-assign if you want to send it back to the pool for an another program committee member to review, if you select this option please add a comment:</label>
                <select class="form-control form-control-lg" name="decision" id="decision">
                    % for key in sorted(decisions.keys(), reverse=True):
                        % if decisions[key] == decision:
                            <option value="{{ key }}" selected="selected">{{ decisions[key] }}</option>
                        % elif not decision and key == 0:
                            <option value="{{ key }}" selected="selected">{{ decisions[key] }}</option>
                        % else:    
                            <option value="{{ key }}" >{{ decisions[key] }}</option>
                        % end 
                    % end    
                </select>
             </div>   
             <div class="form-group">
                <label for="">Confidential remarks for program committee:</label>
                <textarea class="form-control" id="comments" name="comments" rows="4" cols="50">{{ comment }}</textarea>
             </div>   
             <div class="form-check">
                <input class="form-check-input" style="margin-left: 0px" type="checkbox" value="Flagged" id="flag" name="flag" {{ flagged }}> </input>
                <label class="form-check-label" for="flag">Flag for discussion by the Program Committee</label>
             </div>   
            <br/>
            <input class="btn btn-primary" type="submit" name="Submit" value="Submit"/>
            <input class="btn btn-primary" type="submit" name="Back" value="Back"/>
        </form>

      </div>
    </main>
<% include('views/footer.tpl') %>
