<html>
  <body>
   <h1>Marteau</h1>

   <h2>Workers</h2>
   %for worker in workers:
   <div>${worker.worker_id} - Queues: ${", ".join(worker.queues)}</div>
   %endfor

   <h2>Jobs</h2>
   %for job in jobs:
   <div>Job:
     ${job}
   </div>
   %endfor

  <h2>Failures</h2>
   %for job in failures:
   <div>
      <h3>${job.job_id}</h3>
      <pre>${get_result(job.job_id)}</pre>
   </div>
   %endfor

<h2>Successes</h2>
   %for job in successes:
   <div>
      <h3>${job.job_id}</h3>
      <pre>${get_result(job.job_id)}</pre>
   </div>
   %endfor



  </body>
</html>
