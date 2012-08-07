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
      <pre>${get_result(job.job_id)[0]['data']}</pre>
   </div>
   %endfor

<h2>Successes</h2>
   %for job in successes:
   <div>
      <h3><a href="/test/${job.job_id}">${job.job_id}</a></h3>
   </div>
   %endfor

   <h2>Workers</h2>
   %for worker in workers:
   <div>${worker.worker_id} - Queues: ${", ".join(worker.queues)}</div>
   %endfor


  </body>
</html>
