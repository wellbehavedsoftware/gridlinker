#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Well Behaved Software ltd
# Written by José Luis Moreno Durán <joseluis@wellbehavedsoftware.com>
# Based on apt module written by Matthew Williams <matthew at flowroute.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#

DOCUMENTATION = '''
---
module: apt_dbus
short_description: Manages apt-packages using the d-bus apt daemon
description:
  - Manages I(apt) packages (such as for Debian/Ubuntu) using D-Bus API.
version_added: "0.0.1"
options:
  package_list:
    description:
      - A package or package list whose state we want to change. This list will be introduced in a json-like format. For each package that we want to change, the fields 'name' and 'state' must be specified.
    required: true
    default: null
  update_cache:
    description:
      - Run the equivalent of C(apt-get update) before the operation. Can be run as part of the package installation or as a separate step.
    required: false
    default: no
    choices: [ "yes", "no" ]
  cache_valid_time:
    description:
      - If C(update_cache) is specified and the last run is less or equal than I(cache_valid_time) seconds ago, the C(update_cache) gets skipped.
    required: false
    default: no

'''

EXAMPLES = '''
# Update repositories cache and install "foo" package
- apt_dbus: package_list="[{'name': 'foo', 'state': 'present'}]" update_cache=yes

# Remove the package "foo"
- apt_dbus: package_list="[{'name': 'foo', 'state': 'absent'}]"

# Install the package "foo"
- apt_dbus: package_list="[{'name': 'foo', 'state': 'present'}]"

# Install the version '1.00' of package "foo"
- apt_dbus: package_list="[{'name': 'foo=1.00', 'state': 'present'}]"

# Upgrade the package "foo"
- apt_dbus: package_list="[{'name': 'foo', 'state': 'upgraded'}]"

# Purge the package "foo"
- apt_dbus: package_list="[{'name': 'foo', 'state': 'purged'}]"

# Install the package "foo" and remove the package "bar"
- apt_dbus: package_list="[{'name': 'foo', 'state': 'present'}, {'name': 'bar', 'state': 'absent'}]"

# 
'''

import traceback
# added to stave off future warnings about apt api
import warnings
warnings.filterwarnings('ignore', "apt API not stable yet", FutureWarning)

import os
import datetime
import fnmatch
import itertools

# APT related constants
APT_ENV_VARS = dict(
  DEBIAN_FRONTEND = 'noninteractive',
  DEBIAN_PRIORITY = 'critical',
  LANG = 'C'
)

APT_GET_ZERO = "0 upgraded, 0 newly installed"
APTITUDE_ZERO = "0 packages upgraded, 0 newly installed"
APT_LISTS_PATH = "/var/lib/apt/lists"
APT_UPDATE_SUCCESS_STAMP_PATH = "/var/lib/apt/periodic/update-success-stamp"

HAS_PYTHON_APT = True
try:
    import apt
    import apt.debfile
    import apt_pkg
except ImportError:
    HAS_PYTHON_APT = False

def package_split(pkgspec):
    parts = pkgspec.split('=', 1)
    if len(parts) > 1:
        return parts[0], parts[1]
    else:
        return parts[0], None

def package_versions(pkgname, pkg, pkg_cache):
    try:
        versions = set(p.version for p in pkg.versions)
    except AttributeError:
        # assume older version of python-apt is installed
        # apt.package.Package#versions require python-apt >= 0.7.9.
        pkg_cache_list = (p for p in pkg_cache.Packages if p.Name == pkgname)
        pkg_versions = (p.VersionList for p in pkg_cache_list)
        versions = set(p.VerStr for p in itertools.chain(*pkg_versions))

    return versions

def package_version_compare(version, other_version):
    try:
        return apt_pkg.version_compare(version, other_version)
    except AttributeError:
        return apt_pkg.VersionCompare(version, other_version)

def package_status(m, pkgname, version, cache, state):
    try:
        # get the package from the cache, as well as the
        # the low-level apt_pkg.Package object which contains
        # state fields not directly acccesible from the
        # higher-level apt.package.Package object.
        pkg = cache[pkgname]
        ll_pkg = cache._cache[pkgname] # the low-level package object
    except KeyError:
        if state == 'install':
            try:
                if cache.get_providing_packages(pkgname):
                    return False, True, False
                m.fail_json(msg="No package matching '%s' is available" % pkgname)
            except AttributeError:
                # python-apt version too old to detect virtual packages
                # mark as upgradable and let apt-get install deal with it
                return False, True, False
        else:
            return False, False, False
    try:
        has_files = len(pkg.installed_files) > 0
    except UnicodeDecodeError:
        has_files = True
    except AttributeError:
        has_files = False  # older python-apt cannot be used to determine non-purged

    try:
        package_is_installed = ll_pkg.current_state == apt_pkg.CURSTATE_INSTALLED
    except AttributeError: # python-apt 0.7.X has very weak low-level object
        try:
            # might not be necessary as python-apt post-0.7.X should have current_state property
            package_is_installed = pkg.is_installed
        except AttributeError:
            # assume older version of python-apt is installed
            package_is_installed = pkg.isInstalled

    if version:
        versions = package_versions(pkgname, pkg, cache._cache)
        avail_upgrades = fnmatch.filter(versions, version)

        if package_is_installed:
            try:
                installed_version = pkg.installed.version
            except AttributeError:
                installed_version = pkg.installedVersion

            # Only claim the package is installed if the version is matched as well
            package_is_installed = fnmatch.fnmatch(installed_version, version)

            # Only claim the package is upgradable if a candidate matches the version
            package_is_upgradable = False
            for candidate in avail_upgrades:
                if package_version_compare(candidate, installed_version) > 0:
                    package_is_upgradable = True
                    break
        else:
            package_is_upgradable = bool(avail_upgrades)
    else:
        try:
            package_is_upgradable = pkg.is_upgradable
        except AttributeError:
            # assume older version of python-apt is installed
            package_is_upgradable = pkg.isUpgradable

    return package_is_installed, package_is_upgradable, has_files

def expand_pkgspec_from_fnmatches(m, pkgspec, cache):
    new_pkgspec = []
    for pkgspec_pattern in pkgspec:
        pkgname_pattern, version = package_split(pkgspec_pattern)

        # note that none of these chars is allowed in a (debian) pkgname
        if frozenset('*?[]!').intersection(pkgname_pattern):
            # handle multiarch pkgnames, the idea is that "apt*" should
            # only select native packages. But "apt*:i386" should still work
            if not ":" in pkgname_pattern:
                try:
                    pkg_name_cache = _non_multiarch
                except NameError:
                    pkg_name_cache = _non_multiarch = [pkg.name for pkg in cache if not ':' in pkg.name]
            else:
                try:
                    pkg_name_cache = _all_pkg_names
                except NameError:
                    pkg_name_cache = _all_pkg_names = [pkg.name for pkg in cache]
            matches = fnmatch.filter(pkg_name_cache, pkgname_pattern)

            if len(matches) == 0:
                m.fail_json(msg="No package(s) matching '%s' available" % str(pkgname_pattern))
            else:
                new_pkgspec.extend(matches)
        else:
            # No wildcards in name
            new_pkgspec.append(pkgspec_pattern)
    return new_pkgspec

def install(m, pkgspec, cache):

    packs = pkgspec.split(' ')
    pkg_list = []

    for package in packs:
        name, version = package_split(package)
        installed, upgradable, has_files = package_status(m, name, version, cache, state='install')
        if not installed or upgradable:
            pkg_list.append("%s" % package)
        if installed and upgradable and version:
            pkg_list.append("%s" % package)
    packages = ' '.join(pkg_list)

    if packages:
        for (k,v) in APT_ENV_VARS.iteritems():
            os.environ[k] = v

        cmd = 'echo y | %s --install "%s"' % (APT_GET_CMD, packages)
        out = os.popen(cmd).read()

        if not "100%" in out:
            return (False, dict(msg="'%s' failed: %s" % (cmd, out), stdout=out, stderr=out))
        else:
            return (True, dict(changed=True, stdout=out, stderr=out))
    else:
        return (True, dict(changed=False, stdout="", stderr=""))

def remove(m, pkgspec, cache):

    packs = pkgspec.split(' ')

    pkg_list = []

    pkgspec = expand_pkgspec_from_fnmatches(m, pkgspec, cache)
    for package in packs:
        name, version = package_split(package)
        installed, upgradable, has_files = package_status(m, name, version, cache, state='remove')
        if installed:
            pkg_list.append("%s" % package)
    packages = ' '.join(pkg_list)

    if not packages:
        return (True, dict(changed=False, stdout="", stderr=""))
    else:

        cmd = 'echo y | %s --remove "%s"' % (APT_GET_CMD, packages)

        for (k,v) in APT_ENV_VARS.iteritems():
            os.environ[k] = v

        out = os.popen(cmd).read()
       
        if not "100%" in out:
            return (False, dict(msg="'%s' failed: %s" % (cmd, out), stdout=out, stderr=out))

        return (True, dict(changed=True, stdout=out, stderr=out))

def purge(m, pkgspec, cache):

    packs = pkgspec.split(' ')

    pkg_list = []

    pkgspec = expand_pkgspec_from_fnmatches(m, pkgspec, cache)
    for package in packs:
        name, version = package_split(package)
        installed, upgradable, has_files = package_status(m, name, version, cache, state='remove')
        if installed or has_files:
            pkg_list.append("%s" % package)
    packages = ' '.join(pkg_list)

    if not packages:
        return (True,dict(changed=False, stdout="", stderr=""))
    else:

        cmd = 'echo y | %s --purge "%s"' % (APT_GET_CMD, packages)

        for (k,v) in APT_ENV_VARS.iteritems():
            os.environ[k] = v

        out = os.popen(cmd).read()
       
        if not "100%" in out:
            return (False, dict(msg="'%s' failed: %s" % (cmd, out), stdout=out, stderr=out))

        return (True, dict(changed=True, stdout=out, stderr=out))

def upgrade(m, pkgspec, cache, system=False):

    packs = pkgspec.split(' ')

    pkg_list = []

    for package in packs:
        name, version = package_split(package)
        installed, upgradable, has_files = package_status(m, name, version, cache, state='install')
        if installed and upgradable:
            pkg_list.append("%s" % package)
        if installed and upgradable and version:
            pkg_list.append("%s" % package)
    packages = ' '.join(pkg_list)

    if packages:
        for (k,v) in APT_ENV_VARS.iteritems():
            os.environ[k] = v

        cmd = 'echo y | %s --upgrade "%s"' % (APT_GET_CMD, packages)
        out = os.popen(cmd).read()

        if not "100%" in out:
            return (False, dict(msg="'%s' failed: %s" % (cmd, out), stdout=out, stderr=out))
        else:
            return (True, dict(changed=True, stdout=out, stderr=out))
    else:
        return (True, dict(changed=False, stdout="", stderr=""))

def main():
    module = AnsibleModule(
        argument_spec = dict(
            update_cache = dict(default=False, aliases=['update-cache'], type='bool'),
            cache_valid_time = dict(type='int'),
            package_list = dict(default=None, aliases=['pkgs', 'names']),
        ),
        required_one_of = [['package_list']],
        supports_check_mode = True
    )

    if not HAS_PYTHON_APT:
        try:
            module.run_command('echo y | aptdcon --install "python-apt"', use_unsafe_shell=True, check_rc=True)
            global apt, apt_pkg
            import apt
            import apt_pkg
        except ImportError:
            module.fail_json(msg="Could not import python modules: apt, apt_pkg. Please install python-apt package.")

    global APTITUDE_CMD
    APTITUDE_CMD = module.get_bin_path("aptitude", False)
    global APT_GET_CMD
    APT_GET_CMD = module.get_bin_path("aptdcon")

    p = module.params
    if not APTITUDE_CMD and p.get('upgrade', None) in [ 'full', 'safe', 'yes' ]:
        module.fail_json(msg="Could not find aptitude. Please ensure it is installed.")

    try:
        cache = apt.Cache()

        if p['update_cache']:
            # Default is: always update the cache
            cache_valid = False
            if p['cache_valid_time']:
                tdelta = datetime.timedelta(seconds=p['cache_valid_time'])
                try:
                    mtime = os.stat(APT_UPDATE_SUCCESS_STAMP_PATH).st_mtime
                except:
                    mtime = False
                if mtime is False:
                    # Looks like the update-success-stamp is not available
                    # Fallback: Checking the mtime of the lists
                    try:
                        mtime = os.stat(APT_LISTS_PATH).st_mtime
                    except:
                        mtime = False
                if mtime is False:
                    # No mtime could be read - looks like lists are not there
                    # We update the cache to be safe
                    cache_valid = False
                else:
                    mtimestamp = datetime.datetime.fromtimestamp(mtime)
                    if mtimestamp + tdelta >= datetime.datetime.now():
                        # dont update the cache
                        # the old cache is less than cache_valid_time seconds old - so still valid
                        cache_valid = True

            if cache_valid is not True:
                cache.update()
                cache.open(progress=None)
            if not p['package_list']:
                module.exit_json(changed=False)

        packages = p['package_list']

        present_packages = ""
        absent_packages = ""
        purged_packages = ""
        upgraded_packages = ""

        #checking which packages have to be installed, removed or purged
        for pack in packages:

            package_name = pack['name']
            package_state = pack['state']

            if package_name.count('=') > 1:
                module.fail_json(msg="invalid package spec: %s" % package)

            if package_state == 'present':
                present_packages += package_name + " "
            elif package_state == 'absent':
                absent_packages += package_name + " "
            elif package_state == 'purged':
                purged_packages += package_name + " "
            elif package_state == 'upgraded':
                upgraded_packages += package_name + " "   
         
        if len(present_packages) != 0:         
            result_install = install(module, present_packages.strip(), cache)
            (success_install, retvals_install) = result_install
        else:
            success_install = True
            retvals_install = dict(changed=False, stdout="", stderr="")

        if len(absent_packages) != 0:   
            result_remove = remove(module, absent_packages.strip(), cache)
            (success_remove, retvals_remove) = result_remove
        else:
            success_remove = True
            retvals_remove = dict(changed=False, stdout="", stderr="")

        if len(purged_packages) != 0: 
            result_purge = purge(module, purged_packages.strip(), cache)
            (success_purge, retvals_purge) = result_purge
        else:
            success_purge = True
            retvals_purge = dict(changed=False, stdout="", stderr="")

        if len(upgraded_packages) != 0: 
            result_upgrade = upgrade(module, upgraded_packages.strip(), cache)
            (success_upgrade, retvals_upgrade) = result_upgrade
        else:
            success_upgrade = True
            retvals_upgrade = dict(changed=False, stdout="", stderr="")

        if success_install and success_remove and success_purge and success_upgrade:
            changed = retvals_install['changed'] or retvals_remove['changed'] or retvals_purge['changed'] or retvals_upgrade['changed']
            output = retvals_install['stdout'] + "\n" + retvals_remove['stdout'] + "\n" + retvals_purge['stdout'] + "\n" + retvals_upgrade['stdout']
            error = retvals_install['stderr'] + "\n" + retvals_remove['stderr'] + "\n" + retvals_purge['stderr'] + "\n" + retvals_upgrade['stderr']

            retvals = dict(changed=changed, stdout=output, stderr=error)

            module.exit_json(**retvals)

        elif not success_install:            
            module.fail_json(**retvals_install)

        elif not success_remove:            
            module.fail_json(**retvals_remove)

        elif not success_purge:            
            module.fail_json(**retvals_purge)

        elif not success_upgrade:            
            module.fail_json(**retvals_upgrade)

    except apt.cache.LockFailedException:
        module.fail_json(msg="Failed to lock apt for exclusive operation")
    except apt.cache.FetchFailedException:
        module.fail_json(msg="Could not fetch updated apt files")

# import module snippets
from ansible.module_utils.basic import *

if __name__ == "__main__":
    main()

# ex: et ts=4 filetype=yaml

