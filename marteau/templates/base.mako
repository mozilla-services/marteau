<!doctype html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <link href='/media/marteau.css' rel='stylesheet' type='text/css'/>
  <link rel="shortcut icon" href="/media/small-logo.png">
  <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
  <script src="https://login.persona.org/include.js" type="text/javascript"></script>
  <script type="text/javascript">${request.persona_js}</script>
  <title>Marteau</title>
</head>
  <body>
    <div id="header">
        <img src="/media/logo.png"/>
        <a href="/" id="title">Marteau</a>
        <span id="subtitle">Hammering your web services since 2012</span>
        <a href="/media/marteau.kar">don't</a>
      <div class="login">
        %if request.user:
         Hi <a href="/profile">${user}</a>.
        %else:
         ${request.persona_button}
        %endif
      </div>

       %if messages:
         %for message in messages:
         <div class="message">
            ${message}
         </div>
       %endfor
     %endif
    </div>
    <div style="clear:both"></div>
     <div id="body">
       ${self.body()}
   </div>

  </body>
</html>
