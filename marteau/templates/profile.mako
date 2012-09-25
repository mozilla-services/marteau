<%inherit file="base.mako"/>

%if not user:
  <a href="/sign">Sign in with Browser-ID</a>
%endif

%if user:

   <h2>Oauth Key</h2>
   %if key:
   <div>Identity
    <pre>${user}</pre>
    </div>
    <div>Secret
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

