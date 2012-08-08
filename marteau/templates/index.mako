<%inherit file="base.mako"/>

<div id="right">
<div id="workers">
<span>Workers</span>
%for worker in workers:
<div>${worker.worker_id} - Queues: ${", ".join(worker.queues)}</div>
%endfor
%if not workers:
Dude. No workers, no chocolate.
%endif
</div>

<div id="form">
<form action="/test" method="POST">
    Add a job. Repo: <input type="text" name="repo"/>
    <input type="submit"/>
</form>
</div>

</div>


<div id="pending">
<h2>Pending jobs</h2>
%for job in jobs:
<div>
<a href="/test/${job.job_id}">${job.job_id}</a>
</div>
%endfor
%if not jobs:
Nothing in my pile.
%endif
</div>

<div id="running">
<h2>Running jobs</h2>
%for job in running:
<div>
    <a href="/test/${job.job_id}">${job.job_id}</a>
</div>
%endfor
%if not running:
I am bored !
%endif
</div>

<div style="clear:both"></div>

<h2>Failures</h2>

<table>
%for job in failures:
<tr>
  <td>${job.job_id}</td>
  <td><a href="/test/${job.job_id}">[Console]</a></td>
</tr>
%endfor
</table>

%if not failures:
None, congrats! &mdash; although that's suspicious.
%endif

<h2>Successes</h2>
<table>
%for job in successes:
<tr>
  <td>${job.job_id}</td>
  <td><a href="/test/${job.job_id}">[Console]</a></td>
  <td><a href="/report/${job.job_id}/index.html">[Funkload Report]</a></td>
</tr>
%endfor
</table>

