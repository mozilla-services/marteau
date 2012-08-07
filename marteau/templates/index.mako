<html>
  <body>
   <h1>Marteau</h1>

    <form action="/test" method="POST">
      Add a job. Repository: <input type="text" name="repo"/>
      <input type="submit"/>
    </form>
   <h2>Pending jobs</h2>
   %for job in jobs:
   <div>
    <a href="/test/${job.job_id}">${job.job_id}</a>
   </div>
   %endfor
    %if not jobs:
    Nothing in my pile
    %endif
   <h2>Running jobs</h2>
   %for job in running:
   <div>
     <a href="/test/${job.job_id}">${job.job_id}</a>
  </div>
   %endfor
    %if not running:
    I am bored !
    %endif


  <h2>Failures</h2>
   %for job in failures:
   <div>
     ${job.job_id} &nbsp; <a href="/test/${job.job_id}">[Console]</a>
   </div>
   %endfor
    %if not failures:
    None, congrats!
    %endif

<h2>Successes</h2>
   %for job in successes:
   <div>
     ${job.job_id} &nbsp; <a href="/test/${job.job_id}">[Console]</a>&nbsp;
     <a href="/report/${job.job_id}/index.html">[Funkload Report]</a>
   </div>
   %endfor

   <h2>Workers</h2>
   %for worker in workers:
   <div>${worker.worker_id} - Queues: ${", ".join(worker.queues)}</div>
   %endfor


  </body>
</html>
