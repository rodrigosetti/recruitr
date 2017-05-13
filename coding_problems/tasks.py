from .models import CodeSubmission
from celery import shared_task
from celery.utils.log import get_task_logger
from subprocess import Popen, PIPE
import os
import tempfile
import uuid

logger = get_task_logger(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))

IMAGE_NAME = 'code-runner'


def kill_and_remove(container_name):
    for action in ('kill', 'rm'):
        p = Popen('docker %s %s' % (action, container_name), shell=True,
                  stdout=PIPE, stderr=PIPE)
        if p.wait() != 0:
            raise RuntimeError(p.stderr.read())


def run_code(code, language, stdin):
    """
    Run code using language interpreter with stdin as input, and return stdout,
    stderr and whether there was a timeout
    Args:
      code: code to run
      language: language of the code (PY, JS, ...)
      stdin: bytes to send over stdin
    Returns:
      Tuple: (stdout, stderr, is_timeout)
    """
    if language == 'PY':
        interpreter = ['python3']
        code_filename = 'input.py'
    elif language == 'JS':
        interpreter = ['nodejs']
        code_filename = 'input.js'
    else:
        raise ValueError("language not supported: %s" % language)

    container_name = uuid.uuid4().hex
    host_code_filename = os.path.join(dir_path, container_name)
    with open(host_code_filename, 'w') as f:
        f.write(code)

    try:
        command = ['gtimeout', '-s', 'SIGKILL', '60',
                   'docker', 'run', '--rm', '--name', container_name,
                   '--network=none', '--read-only', '--interactive',
                   '--volume=%s:/workspace/%s:ro' % (host_code_filename, code_filename),
                   IMAGE_NAME]
        command.extend(interpreter)
        command.append(code_filename)

        logger.info(' '.join(command))

        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        (stdout, stderr) = p.communicate(stdin)
        is_timeout = p.wait() == -9  # Happens on timeout

        if is_timeout:
            # We have to kill the container since it still runs
            # detached from Popen and we need to remove it after because
            # --rm is not working on killed containers
            kill_and_remove(container_name)

        return (stdout, stderr, is_timeout)
    finally:
        os.unlink(host_code_filename)


@shared_task
def judge_code_submission(code_submission_id):
    """
    Execute the coding problem, update it's result in
    place.
    Args:
      code_submission_id: models.CodeSubmission.id
    """
    code_submission = CodeSubmission.objects.get(id=code_submission_id)

    logger.info("Judging code submission: %s" % code_submission)

    code_submission.status = 'R'  # status=RUNNING
    code_submission.save()

    # create a temp folder with all input files
    for input_output in code_submission.problem.inputoutput_set.all():
        logger.info("Running input/output: %s" % input_output)
        (stdout, stderr, is_timeout) = run_code(code_submission.code,
                                                code_submission.language,
                                                input_output.input.encode('utf-8'))

        code_submission.error_output = stderr.decode('utf-8')[-1000:]

        if is_timeout:
            logger.info("timeout")
            code_submission.status = 'T'  # status=TIMEOUT
            break
        elif stderr:
            logger.info("error")
            code_submission.status = 'E'  # status=ERROR
            break
        elif len(stdout) > 1024*1024*5:
            logger.info("output too large")
            code_submission.status = 'L'  # status=OUTPUT TOO LARGE
            break
        elif stdout.decode('utf-8').strip() != input_output.output.strip():
            logger.info("failure")
            code_submission.status = 'F'  # status=FAILURE
            break

    else:
        logger.info("success")
        code_submission.status = 'S'  # status=SUCCESS

    code_submission.save()
