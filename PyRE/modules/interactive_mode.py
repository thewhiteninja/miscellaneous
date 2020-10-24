import cmd
import os
import sys

from modules import debugger
from modules import logger
from modules import utils


class CmdHandler(cmd.Cmd):
    prompt = 'pyre> '

    def __init__(self, args=None, plugins=None, prompt=None):
        if not plugins:
            plugins = {}
        cmd.Cmd.__init__(self)
        if prompt:
            self.prompt = prompt
        self.__cmd_list = [method[3:] for method in dir(self) if callable(getattr(self, method)) and
                           method.startswith("do_") and method != "do_EOF"]

        self.plugins = plugins
        self.dbg = debugger.Debugger()
        self.args = args

        if self.args.executable_filename:
            self.do_load(self.args.executable_filename)

    def precmd(self, line):
        s = line.split(" ")
        possible_cmds = [command for command in self.__cmd_list if command.startswith(s[
                                                                                      0].strip())]
        if len(possible_cmds) == 1:
            s[0] = possible_cmds[0]
            return " ".join(s)
        return line

    def do_def(self, line):
        code = ""
        while True:
            try:
                code += raw_input() + "\n"
            except EOFError:
                break
        try:
            exec code
        except Exception as e:
            logger.logWarn("Exception :" + str(e))

    def do_help(self, args):
        """Get help on commands
           'help' or '?' with no arguments prints a list of commands for which help is available
           'help <command>' or '? <command>' gives help on <command>
        """
        return cmd.Cmd.do_help(self, args)

    def do_quit(self, line):
        """Quit"""
        self.dbg.terminate()
        logger.logInfo("Exited")
        sys.exit(0)

    def do_shell(self, line):
        """Run a shell command"""
        if len(line.strip()) > 0:
            print os.popen(line).read()

    def do_EOF(self, line):
        """Quit"""
        print
        self.do_quit(line)

    def do_load(self, line):
        """Load a new binary"""
        self.dbg.load(line, "")
        if self.dbg.loaded:
            self.prompt = 'pyre(%s)> ' % (os.path.basename(line))

    def do_reload(self, line):
        """Reload a new binary with new arguments"""
        self.dbg.terminate()
        self.dbg.load(line, "")
        if self.dbg.loaded:
            self.prompt = 'pyre(%s)> ' % (os.path.basename(line))

    def do_run(self, line):
        """Run a loaded binary"""
        self.dbg.run()
        if not self.dbg.loaded:
            self.prompt = 'pyre> '

    def do_unload(self, line):
        """Terminate loaded binary"""
        self.dbg.terminate()
        if not self.dbg.loaded:
            self.prompt = 'pyre> '

    def do_breakpoint(self, line):
        """Set a software breakpoint at specified address"""
        self.dbg.set_breakpoint(utils.read_number(line))

    def do_continue(self, line):
        """Continue"""
        self.dbg.resume()

    def do_plugin(self, line):
        """Run a plugin"""
        pluginName = None
        params = []
        tok = line.split(' ')
        if len(tok) > 0:
            pluginName = tok[0]
        if len(tok) > 1:
            params = [p for p in tok[1:] if len(p) > 0]
        if pluginName:
            if self.plugins.has_key(pluginName):
                if len(params) == 0:
                    print "%s : %s" % (self.plugins[pluginName].name, self.plugins[pluginName].descriptionShort)
                    print "Options : "
                    print self.plugins[pluginName].help
                else:
                    self.plugins[pluginName].call(self, params)
            else:
                logger.logInfo("No plugin named %s loaded" % pluginName)
        else:
            for p in self.plugins.values():
                print "%s : %s" % (p.name, p.descriptionShort)

    def complete_plugin(self, text, line, begidx, endidx):
        if not text:
            return sorted([a.name for a in self.plugins.values()])
        else:
            return sorted([f for f in [a.name for a in self.plugins.values()] if f.startswith(text)])

    def do_show(self, line):
        """Show various information"""
        if line == "breakpoints":
            pass
        elif line == "registers":
            ctx = self.dbg.context
            print ctx
            print "EIP : %08x" % ctx.Eip
        elif line == "stack":
            pass
        else:
            if len(line.strip()) > 0:
                logger.logWarn("Undefined information to show")

    def complete_show(self, text, line, begidx, endidx):
        SHOWS = ["breakpoints", "stack", "registers"]
        if not text:
            return SHOWS[:]
        else:
            return [f for f in SHOWS if f.startswith(text)]
