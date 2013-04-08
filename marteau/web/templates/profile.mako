<%inherit file="base.mako"/>

%if not user:
  <a href="/sign">Sign in with Browser-ID</a>
%endif

%if user:
   <h2>MACAuth Key</h2>
   %if key:
   <div>MACAUTH_USER
    <pre>${user}</pre>
    </div>
    <div>MACAUTH_SECRET
    <pre>${key}</pre>
    </div>
    <form method="POST">
      <input name="generate" type="submit" value="Regenerate a new key"></input>
    </form>
   %endif

   %if not key:
    <form method="POST">
      <input name="generate"  type="submit" value="Generate a key"></input>
    </form>

   %endif

   <h2>Registered hosts</h2>
   %for host in hosts:
      <div>
         <form method="DELETE" action="/hosts/${host.name}">
           <strong>${host.name}</strong>
           <input name="revoke" type="submit" value="Revoke"></input>
         </form>

         <pre>${host.key}</pre>
      </div>  
   %endfor

   <form method="POST" action="/hosts">
      <label for="host">Host: </label><input type="text" name="host" value=""/>
      <input name="register" type="submit" value="Register"></input>
   </form>

%endif

