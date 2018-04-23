<%inherit file="base.mako" />

${pkgname} could refer to these repos:

<ul>
    %for repo_name in repo_names:
        <li><a href="/repo/${repo_name}">${repo_name}</a></li>
    %endfor
</ul>
