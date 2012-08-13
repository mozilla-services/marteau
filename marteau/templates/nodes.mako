<%inherit file="base.mako"/>


<div class="smallform resource">
<form action="/nodes" method="POST">
    <span>Add a node.</span>
    <div>
    <input type="text" name="name"/>
    <input type="submit"/>
    </div>
</form>
</div>

   <p>Manage here all nodes used for the tests</p>
 <div>
    %if not nodes:
    Nooooo.... No nodes!
    %endif
    %if nodes:
    <table class="nodes">
        <tr>
            <th>Name</th>
            <th>Enabled?</th>
            <th>Status</th>
            <th/>
        </tr>
        %for node in nodes:
        <tr>
            <td>${node.name}</td>
            <td>
            <a href="/nodes/${node.name}/enable">
              %if node.enabled:
              Enabled
              %endif
               %if not node.enabled:
              Disabled
              %endif
              </a>
            </td>
            <td>${node.status}</td>
            <td>
              <form action="/nodes/${node.name}" method='DELETE'>
                <input type="submit" name="delete" value="delete"/>
              </form>
            </td>
        </tr>
        %endfor
    </table>
%endif

</div>
