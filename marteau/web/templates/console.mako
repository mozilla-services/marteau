<%inherit file="base.mako"/>
<div class="actions">
 <table class='nodes'>
  <tr>
    <th>Status</th>
    <td>${status}</td>
  </tr>
  <tr>
    <th>Created</th>
    <td>${time2str(job.metadata.get('created'))}</td>
  </tr>
  %if 'started' in job.metadata:
 <tr>
    <th>Started</th>
    <td>${time2str(job.metadata.get('started'))}</td>
  </tr>
  %endif
  %if 'ended' in job.metadata:
  <tr>
    <th>Ended</th>
    <td>${time2str(job.metadata.get('ended'))}</td>
  </tr>
   %endif
 </table>
</div>

<div class="actions">
  %if report:
  <a class="label" href="/report/${job.job_id}/index.html">Report</a>
  %endif
  <a class="label" href="/test/${job.job_id}/delete">Delete</a>
  <a class="label" href="/test/${job.job_id}/replay">Replay</a>
</div>


<div style="clear: both"/>
<pre>${console}</pre>
