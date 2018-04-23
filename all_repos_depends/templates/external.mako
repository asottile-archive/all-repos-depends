<%inherit file="base.mako" />

<h2>external package: ${pkgname}</h2>

<h3>reverse dependencies:</h3>

<ul>
    %for repo_name, depend in rdepends:
        <li>
            <a href="/repo/${repo_name}">${repo_name}</a>
            ${depend.package_key}${depend.spec} (${depend.relationship})
        </li>
    %endfor
</ul>
