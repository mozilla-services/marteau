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
%endif

