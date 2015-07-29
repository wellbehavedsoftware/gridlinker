#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Well Behaved Software ltd
# Written by José Luis Moreno Durán <joseluis@wellbehavedsoftware.com>
# Based on apt module written by Matt Wright <matt@nobien.net>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

import tempfile
import os
import json

DOCUMENTATION = '''
---
module: pip
short_description: Manages Python library dependencies in a fast way.
description:
     - "Manage Python library dependencies. To use this module, one of the following keys is required: C(name)
       or C(requirements)."
version_added: "0.7"
options:
  names:
    description:
       - A python library or python library list whose state we want to change. This list will be introduced in a json-like format. For each package that we want to change, the fields 'name' and 'state' must be specified. If we want to install a library, the field 'version' should be also specified.
    required: false
    default: null
  requirements:
    description:
      - The path to a pip requirements file
    required: false
    default: null
  virtualenv:
    description:
      - An optional path to a I(virtualenv) directory to install into
    required: false
    default: null
  virtualenv_site_packages:
    version_added: "1.0"
    description:
      - Whether the virtual environment will inherit packages from the
        global site-packages directory.  Note that if this setting is
        changed on an already existing virtual environment it will not
        have any effect, the environment must be deleted and newly
        created.
    required: false
    default: "no"
    choices: [ "yes", "no" ]
  virtualenv_command:
    version_aded: "1.1"
    description:
      - The command or a pathname to the command to create the virtual
        environment with. For example C(pyvenv), C(virtualenv),
        C(virtualenv2), C(~/bin/virtualenv), C(/usr/local/bin/virtualenv).
    required: false
    default: virtualenv
  extra_args:
    description:
      - Extra arguments passed to pip.
    required: false
    default: null
    version_added: "1.0"
  chdir:
    description:
      - cd into this directory before running the command
    version_added: "1.3"
    required: false
    default: null
  executable:
    description:
      - The explicit executable or a pathname to the executable to be used to
        run pip for a specific version of Python installed in the system. For
        example C(pip-3.3), if there are both Python 2.7 and 3.3 installations
        in the system and you want to run pip for the Python 3.3 installation.
    version_added: "1.3"
    required: false
    default: null
notes:
   - Please note that virtualenv (U(http://www.virtualenv.org/)) must be installed on the remote host if the virtualenv parameter is specified and the virtualenv needs to be initialized.
requirements: [ "virtualenv", "pip" ]
author: Matt Wright
'''

EXAMPLES = '''
# Remove the library "foo"
- fast_pip: names="[{'name': 'foo', 'state': 'absent'}]"

# Install the version '1.00' of library "foo"
- fast_pip: names="[{'name': 'foo', 'version': '1.00', 'state': 'present'}]"

# Install the library "foo" and remove the library "bar"
- fast_pip: names="[{'name': 'foo', 'version': '1.00', 'state': 'present'}, {'name': 'bar', 'state': 'absent'}]"

# 
'''

def _get_cmd_options(module, cmd):
    thiscmd = cmd + " --help"
    rc, stdout, stderr = module.run_command(thiscmd)
    if rc != 0:
        module.fail_json(msg="Could not get output from %s: %s" % (thiscmd, stdout + stderr))

    words = stdout.strip().split()
    cmd_options = [ x for x in words if x.startswith('--') ]
    return cmd_options
    

def _get_full_name(name, version=None):
    if version is None:
        resp = name
    else:
        resp = name + '==' + version
    return resp

def _is_present(name, version, installed_pkgs, state):

    try:
        if installed_pkgs[name] and state == 'absent':
            return True
        elif installed_pkgs[name] and state != 'absent':
            if installed_pkgs[name] == version:
                return True
            else:
                return False
        else:
            return False
    except KeyError:
        return False

def _get_installed_packages(installed_pkgs):

    installed = {}

    for pkg in installed_pkgs:
        if '==' not in pkg:
            continue

        [pkg_name, pkg_version] = pkg.split('==')

        installed.update({pkg_name: pkg_version})

    return installed


def _get_pip(module, env=None, executable=None):
    # On Debian and Ubuntu, pip is pip.
    # On Fedora18 and up, pip is python-pip.
    # On Fedora17 and below, CentOS and RedHat 6 and 5, pip is pip-python.
    # On Fedora, CentOS, and RedHat, the exception is in the virtualenv.
    # There, pip is just pip.
    candidate_pip_basenames = ['pip', 'python-pip', 'pip-python']
    pip = None
    if executable is not None:
        if os.path.isabs(executable):
            pip = executable
        else:
            # If you define your own executable that executable should be the only candidate.
            candidate_pip_basenames = [executable]
    if pip is None:
        if env is None:
            opt_dirs = []
        else:
            # Try pip with the virtualenv directory first.
            opt_dirs = ['%s/bin' % env]
        for basename in candidate_pip_basenames:
            pip = module.get_bin_path(basename, False, opt_dirs)
            if pip is not None:
                break
    # pip should have been found by now.  The final call to get_bin_path will
    # trigger fail_json.
    if pip is None:
        basename = candidate_pip_basenames[0]
        pip = module.get_bin_path(basename, True, opt_dirs)
    return pip


def _fail(module, cmd, out, err):
    msg = ''
    if out:
        msg += "stdout: %s" % (out, )
    if err:
        msg += "\n:stderr: %s" % (err, )
    module.fail_json(cmd=cmd, msg=msg)


def main():
    state_map = dict(
        present='install',
        absent='uninstall -y',
        latest='install -U',
    )

    module = AnsibleModule(
        argument_spec=dict(
            names=dict(default=None, required=False),
            requirements=dict(default=None, required=False),
            virtualenv=dict(default=None, required=False),
            virtualenv_site_packages=dict(default='no', type='bool'),
            virtualenv_command=dict(default='virtualenv', required=False),
            use_mirrors=dict(default='yes', type='bool'),
            extra_args=dict(default=None, required=False),
            chdir=dict(default=None, required=False),
            executable=dict(default=None, required=False),
        ),
        required_one_of=[['names', 'requirements']],
        mutually_exclusive=[['name', 'requirements']],
        supports_check_mode=True
    )

    packages = module.params['names']
    requirements = module.params['requirements']
    extra_args = module.params['extra_args']
    chdir = module.params['chdir']

    err = ''
    out = ''

    env = module.params['virtualenv']
    virtualenv_command = module.params['virtualenv_command']

    if env:
        env = os.path.expanduser(env)
        if not os.path.exists(os.path.join(env, 'bin', 'activate')):
            if module.check_mode:
                module.exit_json(changed=True)

            virtualenv = os.path.expanduser(virtualenv_command)
            if os.path.basename(virtualenv) == virtualenv:
                virtualenv = module.get_bin_path(virtualenv_command, True)

            if module.params['virtualenv_site_packages']:
                cmd = '%s --system-site-packages %s' % (virtualenv, env)
            else:
                cmd_opts = _get_cmd_options(module, virtualenv)
                if '--no-site-packages' in cmd_opts:
                    cmd = '%s --no-site-packages %s' % (virtualenv, env)
                else:
                    cmd = '%s %s' % (virtualenv, env)
            this_dir = tempfile.gettempdir()
            if chdir:
                this_dir = os.path.join(this_dir, chdir)
            rc, out_venv, err_venv = module.run_command(cmd, cwd=this_dir)
            if rc != 0:
                _fail(module, cmd, out_venv, err_venv)

    pip = _get_pip(module, env, module.params['executable'])

    # If there's a virtualenv we want things we install to be able to use other
    # installations that exist as binaries within this virtualenv. Example: we 
    # install cython and then gevent -- gevent needs to use the cython binary, 
    # not just a python package that will be found by calling the right python. 
    # So if there's a virtualenv, we add that bin/ to the beginning of the PATH
    # in run_command by setting path_prefix here.
    path_prefix = None
    if env:
        path_prefix="/".join(pip.split('/')[:-1])

    #create dict with installed packages

    this_dir = tempfile.gettempdir()
    freeze_cmd = '%s freeze' % pip
    rc, out_freeze, err_freeze = module.run_command(freeze_cmd, cwd=this_dir)

    if rc != 0:
        module.exit_json(changed=True)

    installed_packages = _get_installed_packages(out_freeze.split())
    totalChanged = False   

    for package in packages:

        #module.fail_json(msg=installed_packages, changed=False)
        name = package['name']
        state = package['state']
        version = "0.0"

        if state != 'absent':
            version = package['version']

        is_present = _is_present(name, version, installed_packages, state)

        if is_present and state == 'present':
            continue

        cmd = '%s %s' % (pip, state_map[state])

        # Automatically apply -e option to extra_args when source is a VCS url. VCS
        # includes those beginning with svn+, git+, hg+ or bzr+
        if name:
            if name.startswith('svn+') or name.startswith('git+') or \
                    name.startswith('hg+') or name.startswith('bzr+'):
                args_list = []  # used if extra_args is not used at all
                if extra_args:
                    args_list = extra_args.split(' ')
                if '-e' not in args_list:
                    args_list.append('-e')
                    # Ok, we will reconstruct the option string
                    extra_args = ' '.join(args_list)

        if extra_args:
            cmd += ' %s' % extra_args
        if name:
            cmd += ' %s' % _get_full_name(name, version)
        elif requirements:
            cmd += ' -r %s' % requirements

        this_dir = tempfile.gettempdir()
        if chdir:
            this_dir = os.path.join(this_dir, chdir)

        rc, out_pip, err_pip = module.run_command(cmd, path_prefix=path_prefix, cwd=this_dir)

        if rc == 1 and state == 'absent' and 'not installed' in out_pip:
            pass  # rc is 1 when attempting to uninstall non-installed package
        elif rc != 0:
            _fail(module, cmd, out_pip, err_pip)

        if state == 'absent':
            changed = 'Successfully uninstalled' in out_pip
        else:
            changed = 'Successfully installed' in out_pip

        msg = "has not changed."
        if changed:
            totalChanged = True
            msg = "has changed."

        out += "The package " + name + " (" + version + ") " + msg
        err += err_pip

    module.exit_json(changed=totalChanged,  stdout=out, stderr=err)

# import module snippets
from ansible.module_utils.basic import *

main()

# ex: et ts=4 filetype=py

