<%inherit file="base.mako"/>

%if request.registry.settings['aws']:
<div>
 <p>Manage your AWS environment.</p>
 <a href="https://console.aws.amazon.com/ec2/v2/home"> <img src="/media/ec2.png"/></a>
</div>

%else:

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
            <th>Owner</th>
            <th/>
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
            <td>${node.owner}</td>
            <td>
              <form action="/nodes/${node.name}/test" method='GET' target="_blank">
                <input type="submit" name="test" value="test connection"/>
              </form>
            </td>
            <td>
              <form action="/nodes/${node.name}" method='DELETE'>
                <input type="submit" name="delete" value="remove"/>
              </form>
            </td>
        </tr>
        %endfor
    </table>
%endif

</div>

%endif
