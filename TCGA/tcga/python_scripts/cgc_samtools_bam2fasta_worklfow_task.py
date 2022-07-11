#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Copyright (c) 2016--, Evguenia Kopylova, Jad Kanbar, SevenBridges dev team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

"""
Create tasks for samtools-bam2fasta-worklfow workflow.
"""

from __future__ import print_function
import logging, yaml
import click
import sevenbridges as sb
from sevenbridges.errors import SbgError
from os.path import join


def load_config(yaml_fp):
    """Load CGC API configuration file.

    Parameters
    ----------
    yaml_fp: str
        Filepath to CGC API configuration file

    Return
    ------
    logger: logger instance
        Log
    """
    try:
        fp = open(yaml_fp)
        config = yaml.load(fp)
    except:
        raise SbgError('%s file missing!' % yaml_fp)

    logger = logging.getLogger('log')
    log_handler = logging.FileHandler(config['log_file'])
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)

    return logger, config


def create_task_bam2fasta_cgc(all_files,
                              logger,
                              task_name,
                              config,
                              api):
    """Create CGC task for samtools-bam2fasta-worklfow workflow.

    Parameters
    ----------
    all_files: list
        TCGA file IDs
    logger: logger instance
        Log
    task_name: str
        CGC task name
    config: dict
        YAML configuration file
    api: SevenBridges Api instance
        Api       
    """
    inputs = {"input_bam_file" : all_files}
    task_name = "bam2fasta_%s" % task_name
    logger.info('\tName: %s' % task_name)
    my_project = api.projects.get(id = config['project'])
    #try:
    #    api.tasks.create(name=task_name,
    #                     project=my_project.id,
    #                     app=config['app-bam2fasta'],
    #                     inputs=inputs,
    #                     description=task_name)
    #except SbgError as e:
    #    logger.error("Draft task was not created!", exc_info=e)
    #    raise SbgError("Draft task was not created!")


def create_tasks(api,
                 logger,
                 config,
                 lower_bound_group_size,
                 upper_bound_group_size):
    """Create draft tasks for samtools-bam2fasta-worklfow workflow.

    Parameters
    ----------
    api: SevenBridges API instance
        Api
    logger: logger instance
        Log
    config: dict
        YAML configuration file
    lower_bound_group_size: int
        Lower bound on total size of input files to pass to workflow
    upper_bound_group_size: int
        Upper bound on total size of input files to pass to workflow
    """
    logger.info('Creating draft tasks.')
    # Retrieve BAM and FASTA files associated with project, disease type,
    # data format experimental strategy and data type
    bam_inputs = list(
        api.files.query(
            project=config['project'],
            metadata={'disease_type': config['disease'],
                      'data_format': ['BAM'],
                      'experimental_strategy': ['RNA-Seq', 'WGS'],
                      'data_type': ['Raw sequencing data']}).all())
    # Loop through BAM files computing total size, create task if size within
    # lower and upper bounds
    total_size_gb = 0.0
    all_files = []
    files_tasked = []
    total_tasks_created = 0
    num_wgs = 0
    num_rna_seq = 0
    for i, file in enumerate(sorted(bam_inputs)):
        file_size_gb = file.size/float(1073741824)
        exp_str = file.metadata['experimental_strategy']
        if exp_str == 'WGS':
            num_wgs += 1
        elif exp_str == 'RNA-Seq':
            num_rna_seq += 1
        else:
            raise ValueError('%s is not supported' % exp_str)
        # If:
        # (1) File will cause total file size to exceed upper limit, then
        # Create task and add file to next task
        if (total_size_gb + file_size_gb > upper_bound_group_size and
                len(all_files) > 1):
            files_tasked.extend(all_files)
            total_tasks_created += 1
            # Add info to logger
            logger.info('Task %s: %s files, %.2f Gb' % (total_tasks_created,
                                                        len(all_files),
                                                        total_size_gb))
            task_name = "%s_%s_task_%s_files_%.2fGb" % (
                config['disease'],
                str(total_tasks_created),
                str(len(all_files)),
                total_size_gb)
            # Create draft tasks for samtools-bam2fasta-workflow workflow
            create_task_bam2fasta_cgc(all_files, logger, task_name, config,
                                      api)
            all_files = []
            total_size_gb = 0.0
        # Add new file to next task
        all_files.append(file)
        total_size_gb += file_size_gb
        # If:
        # (1) Single file larger than upper bound limit, or
        # (2) Group of files fall within defined limit, or
        # (3) Last file encountered, then
        # Create task.
        if ( (len(all_files) == 1 and
                total_size_gb >= upper_bound_group_size) or
                (total_size_gb > lower_bound_group_size and
                total_size_gb < upper_bound_group_size) or
                i+1 == len(bam_inputs) ):
            files_tasked.extend(all_files)
            total_tasks_created += 1
            # Add info to logger
            logger.info('Task %s: %s files, %.2f Gb' % (total_tasks_created,
                                                        len(all_files),
                                                        total_size_gb))
            task_name = "%s_%s_task_%s_files_%.2fGb" % (
                config['disease'],
                str(total_tasks_created),
                str(len(all_files)),
                total_size_gb)
            # Create draft tasks for samtools-bam2fasta-workflow workflow
            create_task_bam2fasta_cgc(all_files, logger, task_name, config,
                                      api)
            all_files = []
            total_size_gb = 0.0
    logger.info('Total tasks created: %s' % str(total_tasks_created))
    logger.info('Total files tasked: %s' % str(len(files_tasked)))
    logger.info('Total files for disease type: %s' % str(len(bam_inputs)))
    logger.info('Total WGS files: %s' % str(num_wgs))
    logger.info('Total RNA-Seq files: %s' % str(num_rna_seq))
    if len(files_tasked) != len(bam_inputs):
        files_not_tasked = []
        for _file in bam_inputs:
            if _file not in files_tasked:
                files_not_tasked.append(
                    (_file.name, _file.size/float(1073741824)))
        raise ValueError('Not all BAM files were added to tasks\n'
                         'MISSING files: %s' % files_not_tasked)


def run_tasks(api,
              logger,
              config):
    """Launch CGC tasks.

    Parameters
    ----------
    api: SevenBridges API instance
        Api
    logger: logger instance
        Log
    config: dict
        YAML configuration file  
    """
    logger.info('Running tasks!')
    project = config['project']
    max_task_number = config['task_max_per_run']
    app = config['app-bam2fasta']
    running_tasks = list(
        api.tasks.query(project=project, limit=100, status='RUNNING').all()
    )
    queued_tasks = list(
        api.tasks.query(project=project, limit=100, status='QUEUED').all()
    )
    if len(running_tasks) + len(queued_tasks) >= max_task_number:
        logger.info("Maximum number of active tasks reached!")
        raise SbgError(
            'Unable to run! You already have {active} active tasks. '
            'Please try later!'.format
            (active=len(running_tasks) + len(queued_tasks)))
    draft_tasks = list(
        api.tasks.query(project=project,
                        limit=100,
                        status='DRAFT').all())
    if len(draft_tasks) == 0:
        print('No draft tasks left to be run!')
        return
    # Remove draft tasks that weren't created by current app
    draft_tasks_app = list(draft_tasks)
    for task in draft_tasks:
        if app not in task.app:
            draft_tasks_app.remove(task)
    executable_tasks = draft_tasks_app[0:max_task_number - len(running_tasks)]
    for task in executable_tasks:
        # Sanity check only current app draft tasks are run
        if app in task.app:
            try:
                task.run()
            except SbgError as e:
                logger.error("Task was not started! Error happened ", exc_info=e)
                raise SbgError('Task was not started! Error happened')
            if task.status == 'DRAFT':
                logger.error("Task was not started! Task state is DRAFT!")
                raise SbgError("Task was not started! Task state is DRAFT!")


def show_status(api):
    """Show CGC status.

    Parameters
    ----------
    api: SevenBridges API instance
        Api
    """
    logger.info('Fetching task statuses!')
    project = config['project']
    queued = api.tasks.query(project=project, status='QUEUED').total
    running = api.tasks.query(project=project, status='RUNNING').total
    completed = api.tasks.query(project=project, status='COMPLETED').total
    draft = api.tasks.query(project=project, status='DRAFT').total
    failed = api.tasks.query(project=project, status='FAILED').total
    aborted = api.tasks.query(project=project, status='ABORTED').total
    print("Draft={}, Queued={}, Running={}, Completed={},"
          " Failed={}, Aborted={} ".format(draft, queued,
                                           running, completed,
                                           failed, aborted)
          )


@click.command()
@click.option('--yaml-fp', required=True,
              type=click.Path(resolve_path=True, readable=True, exists=False,
                              file_okay=True),
              help='Filepath to output CGC API yaml file')
@click.option('--create-draft-tasks', required=True, type=bool, default=False,
              show_default=True, help='Create CGC draft tasks')
@click.option('--run-draft-tasks', required=False, type=bool, default=False,
              show_default=False, help='Run CGC draft tasks')
@click.option('--check-status', required=False, type=bool, default=False,
              show_default=True, help='Show CGC task status')
@click.option('--lower-bound-group-size', required=False, type=int,
              default=400, show_default=True,
              help='Lower bound on total size of input files to pass to '
              'workflow')
@click.option('--upper-bound-group-size', required=False, type=int,
              default=600, show_default=True,
              help='Upper bound on total size of input files to pass to '
              'workflow')
def main(yaml_fp,
         create_draft_tasks,
         run_draft_tasks,
         check_status,
         lower_bound_group_size,
         upper_bound_group_size):
    logger, config = load_config(yaml_fp)
    sb_config = sb.Config(url=config['api-url'], token=config['token'])
    api = sb.Api(config=sb_config)

    if create_draft_tasks:
        create_tasks(api, logger, config, lower_bound_group_size,
                     upper_bound_group_size)
    elif run_draft_tasks:
        run_tasks(api, logger, config)
    elif check_status:
        show_status(api)
    else:
        raise ValueError('Please select one of --create-draft-tasks, '
                         '--run-draft-tasks or --check-status')


if __name__ == "__main__":
    main()
