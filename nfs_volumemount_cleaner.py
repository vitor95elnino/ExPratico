#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse and remove volume dictionary from the yaml configuration file
for the given TLA"""

from optparse import OptionParser
import os
import sys

from git import Repo
from git.exc import GitCommandError
import gitlab
from ruamel.yaml import YAML

yaml = YAML()
yaml.explicit_start = True
yaml.preserve_quotes = True
yaml.allow_duplicate_keys = True
# yaml.boolean_representation = ['False', 'True']

VOLUME_CONFIG_LOCATION = 'rsyslog-server/oslg'
GITLAB_URL = 'https://gitlab.app.betfair/'
REPO_ID = 10370  # devops/monitoring


class ParserChecker:
    def __init__(self, args, options):
        self.tla = args[0]
        self.az = args[1]
        self.dc = args[2]
        self.voldir = args[3]


def parse_volume_mount_config(checker, in_file):
    """Parse the volume mounting point configuration"""

    with open(in_file, 'r') as f:
        data = yaml.load(f)
    mount_key_name = f'vol_{checker.dc}_nfs_{checker.tla}_{checker.az}'
    tla_mount = data['mounts'].pop(mount_key_name, None)

    if tla_mount:
        print(
            f'Info: Removing {mount_key_name} mounting point block from '
            f'{in_file}')
        with open(in_file, 'w') as f:
            parse_data = yaml.dump(data, f)
        return True
    else:
        print(
            f'Info: No volume mounting point could be found for {checker.tla}')
        return False


def git_checkout(branch_name, repo):
    """Checking out exisiting or create a new branch"""
    try:
        repo.git.rev_parse(f'remotes/origin/{branch_name}', verify=True,
                           quiet=True)
        repo.git.checkout(branch_name)
        print('checked out exisiting branch ....')
    except GitCommandError:
        repo.git.checkout('HEAD', b=branch_name)
        print('New branch created .....')


def push_git_change(checker, in_file, branch_name, repo):
    """Add, commit and push"""
    repo.git.add(in_file)
    repo.git.commit(
        m=f'Demmissionining {checker.tla} from configuration file {in_file}')
    repo.git.push('origin', branch_name, set_upstream=None)


def create_mr(checker, branch_name):
    """Raising Merge Request in gitlab"""
    gitlab_token = os.getenv('GITLAB_TOKEN')
    if not gitlab_token:
        print(
            f'ERROR: Gitlab token is not set. Skipping the merge request '
            f'creation for NFS mounts configuration file ...')
        sys.exit(1)

    with gitlab.Gitlab(GITLAB_URL, private_token=gitlab_token) as gl:
        monitoring_project = gl.projects.get(REPO_ID)
        mrs = monitoring_project.mergerequests.list(state='opened')
        mrs_branch = [mr for mr in mrs if mr.source_branch == branch_name]
        if mrs_branch:
            mr_branch = mrs_branch[0]
            mr_branch.description = f'{mr_branch.description}\n\n{checker.dc} ' \
                                    f'{checker.az}'
            mr_branch.save()
        else:
            mr_branch = monitoring_project.mergerequests.create(
                {'source_branch': branch_name,
                 'target_branch': 'master',
                 'title': f'Decommissioning NFS volume '
                          f'mount for {checker.tla}',
                 'description': f'{checker.dc} {checker.az}'
                 })

    return mr_branch.iid, mr_branch.web_url


def main():
    usage = 'usage: %prog <tla> <availability_zone> <dc> <volume_config_dir>'
    parser = OptionParser(usage=usage,
                          description='Parse and remove volume dictionary '
                                      'from the yaml configuration file for '
                                      'the given TLA',
                          version='%prog 1.0')
    (options, args) = parser.parse_args()
    if len(args) != 4:
        parser.error(
            f'ERROR: Wrong number of arguments. Argument list: {args}')

    # Given arguments
    checker = ParserChecker(args, options)

    # File to be changed
    in_file = os.path.join(checker.voldir, VOLUME_CONFIG_LOCATION, checker.dc,
                           f'{checker.az}.yml')
    branch_name = f'decomm_{checker.tla}'
    if not os.path.isfile(in_file):
        print(
            f'ERROR: The volume mounting configuration file {in_file} '
            f'does not exist.')
        sys.exit(1)

    # git object
    repo = Repo(checker.voldir)
    git_checkout(branch_name, repo)
    # Parse the volume mounting configuration file
    file_changed = parse_volume_mount_config(checker, in_file)
    if file_changed:
        push_git_change(checker, in_file, branch_name, repo)
        mr_id, mr_url = create_mr(checker, branch_name)
        #  if you change the next line you'll need to change
        #  tla_decommission_job because this is used to close the
        #  merge_request automatically
        print(f'nfs_merge_request_id:{mr_id}')
        print(
            f'Info: Please follow this merge request link in order to review '
            f'the changes, prior to merging to master: {mr_url}')

    sys.exit(0)


if __name__ == '__main__':
    main()
