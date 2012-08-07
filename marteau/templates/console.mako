<html>
  <body>
   <h1>Marteau</h1>
   <h2>Status: ${status}</h2>
   %if report:
       <a href="${report}">Full Funkload report.</a>
   %endif

   <pre>${console}</pre>
  </body>
</html>
