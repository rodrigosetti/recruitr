from .models import CodeSubmission
from celery import shared_task
from celery.utils.log import get_task_logger
from subprocess import Popen, PIPE
import os
from itertools import count
import platform
import uuid

logger = get_task_logger(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))

IMAGE_NAME = 'runner'


def kill_and_remove(container_name):
    for action in ('kill', 'rm'):
        p = Popen('docker %s %s' % (action, container_name), shell=True,
                  stdout=PIPE, stderr=PIPE)
        if p.wait() != 0:
            raise RuntimeError(p.stderr.read())


timeout_cmd = 'gtimeout' if platform.system() == 'Darwin' else 'timeout'


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

    read_only = True
    if language == 'PY':
        interpreter = ['python3']
        filename = 'code.py'
    elif language == 'JS':
        interpreter = ['nodejs']
        filename = 'code.js'
    elif language == 'HA':
        interpreter = ['runhaskell']
        filename = 'code.hs'
        read_only = False
    elif language == 'PE':
        interpreter = ['perl']
        filename = 'code.pl'
    elif language == 'RU':
        interpreter = ['ruby']
        filename = 'code.rb'
    elif language == 'SH':
        interpreter = ['bash']
        filename = 'code.sh'
    elif language == 'SC':
        interpreter = ['scala']
        filename = 'code.scala'
    elif language == 'C':
        interpreter = ['run-c']
        filename = 'code.c'
        read_only = False
    elif language == 'CP':
        interpreter = ['run-cpp']
        filename = 'code.cpp'
        read_only = False
    elif language == 'JA':
        interpreter = ['run-java']
        filename = 'Main.java'
        read_only = False
    elif language == 'PH':
        interpreter = ['php']
        filename = 'code.php'
    elif language == 'RA':
        interpreter = ['racket']
        filename = 'code.rkt'
    else:
        raise ValueError("language not supported: %s" % language)

    container_name = uuid.uuid4().hex
    host_code_filename = os.path.join(dir_path, container_name)
    with open(host_code_filename, 'w') as f:
        f.write(code)

    try:
        command = [timeout_cmd, '-s', 'SIGKILL', '60',
                   'docker', 'run', '--rm', '--name', container_name,
                   '--network=none', '--interactive',
                   '--volume={}:/workspace/{}:ro'.format(host_code_filename, filename)]

        if read_only:
            command.append('--read-only')

        command.append(IMAGE_NAME)

        command.extend(interpreter)
        command.append(filename)

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
    for ion, input_output in enumerate(code_submission.problem.inputoutput_set.all()):
        logger.info("Running input/output: %s" % input_output)

        for t in range(input_output.times):

            if input_output.dynamic_input:
                (stdout, stderr, is_timeout) = run_code(input_output.input, 'PY', b'')
                if is_timeout:
                    logger.error("Unexpected timeout when evaluating dynamic input of %s" % input_output)
                    continue
                if stderr:
                    logger.error("Unexpected error when evaluating dynamic input of %s" % input_output)
                    logger.error(stderr)
                    continue

                input_text = stdout.decode('utf-8')
            else:
                input_text = input_output.input

            input_bytes = input_text.encode('utf-8')

            if input_output.dynamic_output:
                (stdout, stderr, is_timeout) = run_code(input_output.output, 'PY', input_bytes)
                if is_timeout:
                    logger.error("Unexpected timeout when evaluating dynamic output of %s" % input_output)
                    continue
                if stderr:
                    logger.error("Unexpected error when evaluating dynamic output of %s" % input_output)
                    logger.error(stderr)
                    continue

                output_text = stdout.decode('utf-8')
            else:
                output_text = input_output.output

            (stdout, stderr, is_timeout) = run_code(code_submission.code,
                                                    code_submission.language,
                                                    input_bytes)

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
            else:
                output_lines = stdout.decode('utf-8').strip().splitlines()
                expected_lines = output_text.strip().splitlines()
                n_output = len(output_lines)
                n_expected = len(expected_lines)

                if n_output != n_expected:
                    failure = True
                    code_submission.error_output = "expected {} lines, but got {}, of case #{}{}".format(n_expected, n_output, ion+1, " (example)" if input_output.example else "")
                    code_submission.status = 'F'  # status=FAILURE
                    break

                failure = False
                for n, output_line, expected_line in zip(count(1), output_lines, expected_lines):
                    logger.debug("\"{}\" == \"{}\"".format(output_line, expected_line))

                    if output_line.strip() != expected_line:
                        logger.info("failure")
                        failure = True
                        code_submission.error_output = "mismatch at line {}, of case #{}{}".format(n, ion+1, " (example)" if input_output.example else "")
                        break

                if failure:
                    code_submission.status = 'F'  # status=FAILURE
                    break

        if code_submission.status != 'R':
            # not running anymore. don't move to next input_output
            break

    # if still running: mark as success
    if code_submission.status == 'R':
        logger.info("success")
        code_submission.status = 'S'  # status=SUCCESS

    code_submission.save()
