<!doctype html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

  <link href='/media/marteau.css' rel='stylesheet' type='text/css'/>
  <link rel="shortcut icon" href="/media/small-logo.png">
  <title>Marteau</title>
</head>
  <body>
    <div id="header">
        <img src="/media/logo.png"/>
        <a href="/" id="title">Marteau</a>
        <span id="subtitle">Hammering your web services since 2012</span>
        <a href="/media/marteau.kar">don't</a>
       %if messages:
         %for message in messages:
         <div class="message">
            ${message}
         </div>
         %endfor
         <div style="clear:both"></div>
       %endif

     </div>
     <div id="body">
       ${self.body()}
   </div>

  </body>
</html>
