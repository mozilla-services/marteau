<%inherit file="base.mako"/>
<h2>Status: ${status}</h2>
%if report:
    <a href="${report}">Full Funkload report.</a>
%endif

<pre>${console}</pre>
