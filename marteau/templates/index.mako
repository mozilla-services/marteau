<html>
  <body>
   <h1>Marteau</h1>

   <h2>Workers</h2>
   %for worker in workers:
   <div>${worker.worker_id} - Queues: ${", ".join(worker.queues)}</div>
   %endfor

   <h2>Pending jobs</h2>
   %for job in jobs:
   <div>
    <h3><a href="/test/${job.job_id}">${job.job_id}</a></h3>
   </div>
   %endfor

   <h2>Running jobs</h2>
   %for job in running:
   <div>
        <h3><a href="/test/${job.job_id}">${job.job_id}</a></h3>
    </div>
   %endfor


  <h2>Failures</h2>
   %for job in failures:
   <div>
      <h3><a href="/test/${job.job_id}">${job.job_id}</a></h3>
      <pre>${get_result(job.job_id)['data']}</pre>
   </div>
   %endfor

<h2>Successes</h2>
   %for job in successes:
   <div>
      <h3><a href="/test/${job.job_id}">${job.job_id}</a></h3>
   </div>
   %endfor


  </body>
</html>
