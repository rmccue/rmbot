import code, threading, sys, traceback, signal, readline

def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message  = "Signal recieved : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)

def dumpstacks(signal, frame):
    """Print stack traces, and continue execution."""
    id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId,""), threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    print "\n".join(code)

# Register appropriate signal handlers.

# SIGTSTP is generated by Ctrl-Z by default. It is intended to pause process
# execution, which is a side effect of dropping into our debug mode anyway.
signal.signal(signal.SIGTSTP, debug) 

# SIGQUIT is generated by Ctrl-\ by default. Its intended use is to kill the
# process with a core dump, but many runtimes i.e. Java use it to dump stack
# traces and then continue execution.
signal.signal(signal.SIGQUIT, dumpstacks) 