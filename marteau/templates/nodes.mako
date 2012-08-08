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
    <table>
        <tr>
            <th>Name</th>
            <th>Enabled</th>
            <th>Status</th>
        </tr>
        %for node in nodes:
        <tr>
            <td>${node.name}</td>
            <td>
              %if node.enabled:
              Enabled.
              %endif
               %if not node.enabled:
              Disabled.
              %endif
            </td>
            <td>${node.status}</td>
        </tr>
        %endfor
    </table>
%endif

</div>
