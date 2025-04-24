from subprocess import Popen, PIPE
import os, sys
import threading
import random
import fcntl
import time

def set_nonblocking(fd):
    """Set the file descriptor to non-blocking mode."""
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

class ThreadReadio(threading.Thread):
    def __init__(self, process, pipe, outfile, term_words, command):
        threading.Thread.__init__(self)
        self.ret = None
        self.process = process
        self.pipe = pipe
        self.outfile = outfile
        self.term_words = term_words
        self.command = command

    def run(self):
        set_nonblocking(self.pipe.fileno())
        content = ""
        while self.process.poll() is None:  # Keep running while process is active
            try:
                text = self.pipe.read().decode("utf-8", errors="replace")
                if text:
                    content = content + text                        
                    to_break = False
                    if content.endswith(self.term_words):
                        to_break = True
                        content = content[:-len(self.term_words)]
                        text = text[:-len(self.term_words)]
                    if self.outfile:
                        print(text, file=self.outfile, end='', flush=True)
                    if to_break:
                        break
            except Exception:
                pass
            time.sleep(0.5)
        self.ret = content


class PShell:
    def __init__(self):
        self.proc = Popen(['bash'], stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)
        self.log_ofile = None
        if 'PSHELL_LOG' in os.environ:
            pshell_log = os.environ['PSHELL_LOG']
            print("Pshell: writing commands to " + pshell_log)
            self.log_ofile = open(pshell_log, 'a')

    def run(self, command, to_print=True, timeout=None):
        if type(command) is list or type(command) is tuple:
            command = " ".join(command)
        secret = random.random()
        term_words = "\n{} done\n".format(secret)
        cmd = command + "; printf \"{}\"; >&2 printf \"{}\"\n".format(term_words, term_words)
        print("PShell.run: " + command)
        if self.log_ofile:
            self.log_ofile.write(command + "\n")
        sys.stdout.flush()
        self.proc.stdin.write(cmd.encode('UTF-8'))
        self.proc.stdin.flush()

        if to_print:
            t1 = ThreadReadio(self.proc, self.proc.stdout, sys.stdout, term_words, command)
            t2 = ThreadReadio(self.proc, self.proc.stderr, sys.stderr, term_words, command)
        else:
            t1 = ThreadReadio(self.proc, self.proc.stdout, None, term_words, command)
            t2 = ThreadReadio(self.proc, self.proc.stderr, None, term_words, command)
        t1.start()
        t2.start()
        # timeout
        if timeout:
            t1.join(timeout)
            t2.join(timeout)
            if t1.is_alive() or t2.is_alive():
                print("PShell.run: killing process")
                self.proc.kill()
                self.proc.wait()
                raise Exception("Timeout")
        else:
            t1.join()
            t2.join()
        return t1.ret, t2.ret


pshell = PShell()


def run(command, to_print=True, timeout=None):
    return pshell.run(command, to_print, timeout)


def update_env(environs, to_print=True):
    for key, val in environs.items():
        pshell.run("export {}={}".format(key, val))


if __name__ == "__main__":
    # run("export TEST=1")
    # run("env | grep TEST")
    run("printf 'hello ' ; sleep 3 ; printf 'world'")