<%inherit file="base.mako"/>

<div id="right">
<div class="resource">
<span>Help</span>
<a href="/docs">Learn how to write a Marteau test</a>
</div>


<div id="form" class="resource">
<form action="/test" method="POST">
 <input type="hidden" name="redirect_url" value="/"/>

 <span>Add a job</span>
 <a href="/addjob">More options</a>
 <table>
    <tr>
      <td>Repo</td>
      <td><input type="text" name="repo"/></td>
    </tr>
    </table>
    <input type="submit"/>
 </table>

</form>
</div>


<div id="workers" class="resource">
<span>Workers</span>
%for worker in workers:
<div>PID : ${worker}</div>
%endfor
%if not workers:
<div>
Dude. No workers, no chocolate.
</div>
%endif
</div>

<div id="nodes" class="resource">
<span>Nodes</span> <a href="/nodes">manage</a>
%for node in nodes:
<div>${node.name}</div>
%endfor
%if not nodes:
<div>
C'mon, I need some boxes.
</div>
%endif
</div>

</div>


<div id="pending">
<h2>Pending jobs</h2>
<table>
%for job in jobs:
<tr>
  <td>${job.metadata.get('repo', job.job_id)} created at ${time2str(job.metadata.get('created'))}</td>
  <td><a class="label" href="/test/${job.job_id}">Console</a></td>
</tr>
%endfor
</table>
%if not jobs:
Nothing in my pile.
%endif
</div>

<div id="running">
<h2>Running jobs</h2>
<table>
%for job in running:
<tr>
  <td>${job.metadata.get('repo', job.job_id)} started at ${time2str(job.metadata.get('started'))}</td>
  <td><a class="label" href="/test/${job.job_id}">Console</a></td>
  <td><a class="label" href="/test/${job.job_id}/cancel">Cancel</a></td>
</tr>
%endfor
</table>
%if not running:
I am bored !
%endif
</div>

<div id="failures">
<h2>Failures</h2>

<table>
%for job in failures:
<tr>
  <td>${job.metadata.get('repo', job.job_id)} ended at ${time2str(job.metadata.get('ended'))}</td>
  <td><a class="label" href="/test/${job.job_id}">Console</a></td>
  <td><a class="label" href="/test/${job.job_id}/delete">Delete</a></td>
  <td><a class="label" href="/test/${job.job_id}/replay">Replay</a></td>
</tr>
%endfor
</table>

%if not failures:
None, congrats! &mdash; although that's suspicious.
%endif
</div>

<div id="successes">
<h2>Successes</h2>
%if successes:
<table>
%for job in successes:
<tr>
  <td>${job.metadata.get('repo', job.job_id)} ended at ${time2str(job.metadata.get('ended'))}</td>
  <td><a class="label" href="/test/${job.job_id}">Console</a></td>
  <td><a class="label" href="/report/${job.job_id}/index.html">Report</a></td>
  <td><a class="label" href="/test/${job.job_id}/delete">Delete</a></td>
  <td><a class="label" href="/test/${job.job_id}/replay">Replay</a></td>
</tr>
%endfor
</table>
%endif

%if not successes:
None, this worries me.
%endif
</div>

