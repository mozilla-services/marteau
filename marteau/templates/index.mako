<%inherit file="base.mako"/>

<div id="right">
<div class="resource">
<span>Help</span>
<a href="/docs">Learn how to write a Marteau test</a>
</div>


<div id="workers" class="resource">
<span>Workers</span>
%for worker in workers:
<div>${worker.worker_id} - Queues: ${", ".join(worker.queues)}</div>
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


<div id="form" class="resource">
<form action="/test" method="POST">
 <input type="hidden" name="redirect_url" value="/"/>

 <span>Add a job</span>
<table>
    <tr>
      <td>Repo</td>
      <td><input type="text" name="repo"/></td>
    </tr>
    <tr>
      <td>Cycles*</td>
      <td><input type="text" name="cycles"/></td>
    </tr>
    <tr>
     <td>Duration*</td>
     <td><input type="text" name="duration"/></td>
    </tr>
    <tr>
      <td>Nodes*</td>
      <td><input type="text" name="nodes"/></td>
    </tr>
    <tr>
      <td>E-Mail to notify*</td>
      <td><input type="text" name="email"/></td>
    </tr>

</table>
    <input type="submit"/>
    <div><italic>*optional</italic></div>

</form>
</div>

</div>


<div id="pending">
<h2>Pending jobs</h2>
%for job in jobs:
<div>
<a href="/test/${job.job_id}">${job.metadata.get('repo', job.job_id)}</a> created at ${time2str(job.metadata.get('created'))}
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
    <a href="/test/${job.job_id}">${job.metadata.get('repo', job.job_id)}</a> started at ${time2str(job.metadata.get('started'))}
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
  <td>${job.metadata.get('repo', job.job_id)} ended at ${time2str(job.metadata.get('ended'))}</td>
  <td><a href="/test/${job.job_id}">[Console]</a></td>
</tr>
%endfor
</table>

%if not failures:
None, congrats! &mdash; although that's suspicious.
%endif

<h2>Successes</h2>
%if successes:
<table>
%for job in successes:
<tr>
  <td>${job.metadata.get('repo', job.job_id)} ended at ${time2str(job.metadata.get('created'))}</td>
  <td><a href="/test/${job.job_id}">[Console]</a></td>
  <td><a href="/report/${job.job_id}/index.html">[Funkload Report]</a></td>
</tr>
%endfor
</table>
%endif

%if not successes:
None, this worries me.
%endif


