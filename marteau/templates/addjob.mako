<%inherit file="base.mako"/>

<h2>Add a job</h2>

<div id="form">
<form action="/test" method="POST" class="job">
 <input type="hidden" name="redirect_url" value="/"/>

  <fieldset>
    <legend>Basic options</legend>
    <ol>
    <li>
      <label for="repo">Repo*</label> <input type="text" name="repo"/>
    </li>
    <li>
      <label for="cycles">Cycles</label>
      <input type="text" name="cycles"/>
    </li>
    <li>
     <label for="duration">Duration</label>
     <input type="text" name="duration"/>
    </li>
    <li>
      <label for="nodes">Nodes</label>
      <input type="text" name="nodes"/>
    </li>
    </ol>

    <div><italic>*required</italic></div>
  </fieldset>
  <fieldset>
    <legend>Advanced options</legend>
    <ol>
      <li>
        <label for="fixture_plugin">Fixture Plugin</label>
        <select id="fixture_plugin" name="fixture_plugin">
        <option value="" selected>No fixture</option>
        %for name, fixture in fixtures:
          <option value="${name}">${fixture.get_name()}</option>
        %endfor
        </select>
      </li>
        <li>
        <label for="fixture_options">Fixture Options</label>
        <input type="text" name="fixture_options"></input>
        </li>
      </ol>
     </fieldset>

  <div style="clear: both"/>
   <div class="buttonsContainer">
    <input type="submit" class="button"/>
   </div>
  <div style="clear: both"/>

</form>
</div>
