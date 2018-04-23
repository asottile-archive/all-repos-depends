<%inherit file="base.mako" />

<h2>repo: ${repo_name}</h2>

%if packages:
    <h3>provided packages</h3>

    <ul>
        %for package in packages:
            <li>${package.name} (${package.type})</li>
        %endfor
    </ul>
%endif

%if depends:
    <h3>dependencies</h3>

    <ul>
        %for depend in depends:
            <li>
                <a href="/pkg/${depend.package_key}">
                    ${depend.package_key}${depend.spec}
                </a>
                (${depend.relationship})
            </li>
        %endfor
    </ul>
%endif

%if rdepends:
    <h3>reverse dependencies</h3>

    <ul>
        %for name, depend in rdepends:
            <li>
                <a href="/repo/${name}">${name}</a>
                ${depend.package_key}${depend.spec} (${depend.relationship})
            </li>
        %endfor
    </ul>
%endif
