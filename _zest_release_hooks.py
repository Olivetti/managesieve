# Copyright 2020-2021 Hartmut Goebel <h.goebel@crazy-compilers.com>
# This file is licensed under the
# GNU Affero General Public License v3 or later (AGPLv3+)
# SPDX-License-Identifier: AGPL-3.0-or-later

import glob
import os
import shutil
import subprocess
import zest.releaser.utils


def sign_release(data):
    "Sign the archive that will be uploaded to PYPI."
    # zest.releaser does a clean checkout where it generates tgz/zip in 'dist'
    # directory and those files will be then uploaded to pypi.
    dist_dir = os.path.join(data['tagdir'], 'dist')
    cmd = ['gpg', '--detach-sign', '--armor']
    codesigning_id = os.getenv("CODESIGNING_ID")
    if codesigning_id:
        print("Using gpg identity", codesigning_id, "for signing.")
        cmd.extend(['--local-user', codesigning_id])
    # Sign all files in the 'dist' directory.
    for f in list(os.listdir(dist_dir)):
        f = os.path.join(dist_dir, f)
        print('Signing file %s' % f)
        subprocess.run(cmd + [f])


def run_twine_check(data):
    import twine.cli
    dist_dir = os.path.join(data['tagdir'], 'dist')
    dist_files = list(glob.glob(os.path.join(dist_dir, "*")))
    twine.cli.dispatch(["check"] + dist_files)


def safe_dist_files(data):
    repo_dist_dir = os.path.join(data['reporoot'], 'dist')
    dist_dir = os.path.join(data['tagdir'], 'dist')
    dist_files = glob.glob(os.path.join(dist_dir, "*"))
    for fn in sorted(os.listdir(dist_dir)):
        src = os.path.join(dist_dir, fn)
        dest = os.path.join(repo_dist_dir, fn)
        if (os.path.exists(dest) and
            not zest.releaser.utils.ask("Overwrite dist/%s" % fn,
                                        default=True)):
            # skip this file
            print("Skipping", fn)
            continue
        print("Saving", fn)
        shutil.copy2(src, dest)
