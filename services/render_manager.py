import subprocess
import threading


_lock = threading.Lock()
_active_processes = {}
_cancelled_jobs = set()


def register_process(job_id, process):
    if not job_id:
        return

    with _lock:
        _active_processes[job_id] = process


def unregister_process(job_id, process=None):
    if not job_id:
        return

    with _lock:
        current = _active_processes.get(job_id)

        if process is None or current is process:
            _active_processes.pop(job_id, None)


def mark_job_started(job_id):
    if not job_id:
        return

    with _lock:
        _cancelled_jobs.discard(job_id)


def is_job_cancelled(job_id):
    if not job_id:
        return False

    with _lock:
        return job_id in _cancelled_jobs


def cancel_job(job_id):
    if not job_id:
        return False

    with _lock:
        _cancelled_jobs.add(job_id)
        process = _active_processes.get(job_id)

    if process is None:
        return True

    try:
        if process.poll() is None:
            process.terminate()

            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
    except OSError:
        pass

    return True


def finish_job(job_id):
    if not job_id:
        return

    with _lock:
        _active_processes.pop(job_id, None)
        _cancelled_jobs.discard(job_id)
