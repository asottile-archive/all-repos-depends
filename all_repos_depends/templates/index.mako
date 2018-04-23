<%!
import json
%>

<%inherit file="base.mako" />

<%block name="title">all-repos-depends</%block>

<h1>all-repos-depends</h1>

search: <input id="search">

<h2>repos</h2>
<div id="repos">
    %for repo in repos:
        <div><a href="/repo/${repo}">${repo}</a></div>
    %endfor
</div>

<h2>packages</h2>
<div id="packages">
    %for package in packages:
        <div><a href="/pkg/${package}">${package}</a></div>
    %endfor
</div>

<h2>external packages</h2>
<div id="external">
    %for package in external:
        <div><a href="/pkg/${package}">${package}</a></div>
    %endfor
</div>

<script>
(function () {
    var repos = ${json.dumps(repos)|n},
        packages = ${json.dumps(packages)|n},
        external = ${json.dumps(external)|n},
        search = document.getElementById('search'),
        reposEl = document.getElementById('repos'),
        packagesEl = document.getElementById('packages'),
        externalEl = document.getElementById('external');

    function norm(s) {
        return s.toLowerCase().replace(/[._-]/g, '-');
    }

    function link(base, s) {
        return '<div><a href="/' + base + '/' + s + '">' + s + '</a></div>';
    }

    function toHtml(base, arr, needle) {
        return arr.filter(function (s) {
            return norm(s).indexOf(needle) >= 0;
        }).map(link.bind(null, base)).join('') || '(no results)';
    }

    function change() {
        var needle = norm(search.value);

        reposEl.innerHTML = toHtml('repo', repos, needle);
        packagesEl.innerHTML = toHtml('pkg', packages, needle);
        externalEl.innerHTML = toHtml('pkg', external, needle);
    }

    search.oninput = search.onchange = search.onpropertychange = change;
    change();
}());
</script>
