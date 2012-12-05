<%inherit file="base.mako"/>

<h2>Add a job</h2>
<script src="/media/jquery.js"></script>
<script src="/media/jquery.textchange.min.js"></script>

<div id="form">
<form action="/test" method="POST" class="job">
 <input type="hidden" name="redirect_url" value="/"/>

  <fieldset>
    <legend>Basic options</legend>
    <ol>
    <li>
      <label for="repo">Repo*</label> <input type="text" name="repo" id="repo"/>
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
      <input type="text" name="nodes" id="nodes"/>
    </li>
    <li>
      <label for="script">Script</label>
      <input type="text" name="script" id="script"/>
    </li>
    <li>
      <label for="test">Test</label>
      <input type="text" name="test" id="test"/>
    </li>


    </ol>

    <div><italic>*required</italic></div>
  </fieldset>
  <fieldset>
    <legend>Advanced options</legend>
    <ol id="options">
      <li id="fixture">
        <label for="fixture_plugin">Fixture Plugin</label>
        <select id="fixture_plugin" name="fixture_plugin">
        <option value="" selected>No fixture</option>
        %for name, fixture in fixtures:
          <option value="${name}">${fixture.get_name()}</option>
        %endfor
        </select>
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

<script>
$(document).ready(function() {

  $("#fixture_plugin").change( function () {
    var selected = $("#fixture_plugin option:selected").val();

    $('#options li').each(function(index) {
       if (this.id !== 'fixture') {
         $(this).remove();
       }
    });

    if (selected != "") {
      $.getJSON("fixture_options/" + selected, function(data) {
        $.each(data.items, function(i, item){
          $('#options').append('<li id="option-' + item.name + '">');
          $('#option-' + item.name).append('<label for="fixture_' + item.name + '">' + item.name  + '</label>');
          $('#option-' + item.name).append('<p>' + item.description + '</p>');
          $('#option-' + item.name).append('<input id="fixture_' + item.name + '" type="text" value="' + item.default + '" name="fixture_' + item.name + '"></input>');

        });
      });

    }
   });

   var timeout;

   $('#repo').bind('textchange', function () {
       clearTimeout(timeout);
       timeout = setTimeout(function () {
         var repo = $("#repo").val();
         $.getJSON("project_options/" + repo, function(data) {
            if (data.hasOwnProperty('nodes'))
                $("#nodes").val(data.nodes);

            if (data.hasOwnProperty('script'))
                $("#script").val(data.script);

            if (data.hasOwnProperty('test'))
                $("#test").val(data.test);
         });

       }, 3000);
    });

});

</script>
