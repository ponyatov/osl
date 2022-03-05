import os, sys

class Object:
    def __init__(self, V):
        self.value = V
        self.nest = []

    def box(self, that):
        if isinstance(that, Object):
            return that
        if isinstance(that, str):
            return S(that)
        raise TypeError(['box', type(that), that])

    def val(self): return f'{self.value}'

    def __format__(self, spec):
        if not spec:
            return self.val()
        raise TypeError(['__format__', spec])

    def __iter__(self): return iter(self.nest)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.nest[idx]
        raise TypeError(['__getitem__', type(idx), idx])

    def __floordiv__(self, that):
        self.nest.append(self.box(that)); return self

class Primitive(Object):
    pass

class S(Primitive):
    def __init__(self, start=None, stop=None, pfx=None, sfx=None):
        super().__init__(start)
        self.start = start; self.stop = stop
        self.pfx = pfx; self.sfx = sfx

    def gen(self, to=None, depth=0):
        ret = ''
        if self.start is not None:
            ret += f'{to.tab*depth}{self.start}\n'
        for i in self:
            ret += i.gen(to, depth + 1)
        if self.stop is not None:
            ret += f'{to.tab*depth}{self.stop}\n'
        return ret

class Sec(S):
    def __init__(self, V=None, pfx=None, sfx=None):
        super().__init__(V)
        self.pfx = pfx; self.sfx = sfx

    def gen(self, to=None, depth=0):
        ret = ''
        if self.nest:
            if self.pfx is not None:
                ret += self.pfx if self.pfx else '\n'
            if self.value is not None:
                ret += f'{to.tab*depth}{to.comment} \\ {self}\n'
            for i in self:
                ret += i.gen(to, depth + 0)
            if self.value is not None:
                ret += f'{to.tab*depth}{to.comment} / {self}\n'
            if self.sfx is not None:
                ret += self.sfx if self.sfx else '\n'
        return ret

class Container(Object):
    def __init__(self, V=''): super().__init__(V)

class Vector(Container):
    pass

class IO(Object):
    def __init__(self, V):
        super().__init__(V)
        self.path = V

class Dir(IO):
    def sync(self):
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass
        for i in self:
            i.sync()

    def __floordiv__(self, that):
        assert isinstance(that, IO)
        that.path = f'{self.path}/{that.path}'
        return super().__floordiv__(that)

class File(IO):
    def __init__(self, V, ext='', tab=' ' * 4, comment='#'):
        super().__init__(V + ext)
        self.ext = ext; self.tab = tab; self.comment = comment
        self.top = Sec()
        self.bot = Sec()

    def sync(self):
        with open(self.path, 'w') as F:
            for i in self.top:
                F.write(i.gen(self))
            for j in self:
                F.write(j.gen(self))
            for k in self.bot:
                F.write(k.gen(self))

class gitiFile(File):
    def __init__(self, V='', ext='.gitignore'):
        super().__init__(V, ext)
        self.bot // '!.gitignore'

class jsonFile(File):
    def __init__(self, V, ext='.json', comment='//'):
        super().__init__(V, ext, comment=comment)

class mkFile(File):
    def __init__(self, V='Makefile', ext='', tab='\t', comment='#'):
        super().__init__(V, ext, tab, comment)

class pyFile(File):
    def __init__(self, V, ext='.py'):
        super().__init__(V, ext)


class mdFile(File):
    def __init__(self, V='README', ext='.md'):
        super().__init__(V, ext)

class readmeFile(mdFile):
    def __init__(self, V='README', p=None):
        super().__init__(V)
        self.p = p

    def sync(self):
        self.nest = []
        (self
         // f'#  {p}'
         // f'## {p.TITLE}'
         // ''
         // p.COPYRIGHT
         // ''
         // f'github: {p.GITHUB}'
         )
        super().sync()


class doxyFile(File):
    def __init__(self, V='doxy', ext='.gen', p=None):
        super().__init__(V, ext)
        self.p = p

    def sync(self):
        self.nest = []
        (self
         // f'PROJECT_NAME           = "{p}"'
         // f'PROJECT_BRIEF          = "{p.TITLE}"'
         // 'PROJECT_LOGO           = doc/logo.png'
         // 'OUTPUT_DIRECTORY       ='
         // 'WARN_IF_UNDOCUMENTED   = NO'
         // f'INPUT                  = README.md {p}.py src doc'
         // 'RECURSIVE              = YES'
         // 'USE_MDFILE_AS_MAINPAGE = README.md'
         // 'HTML_OUTPUT            = docs'
         // 'GENERATE_LATEX         = NO'
         // 'EXTENSION_MAPPING      = ino=C++'
         // 'EXTRACT_ALL            = YES')
        super().sync()


class Meta(Object):
    pass

class Project(Meta):
    def __init__(self, V=None):
        if not V:
            V = os.getcwd().split('/')[-1]
        super().__init__(V)
        self.dirs()
        self.vscode()
        self.mk()
        self.cf()
        self.apt()
        self.reqs()
        self.metainfo()
        self.readme()
        self.doxy()
        self.py()

    def metainfo(self):
        self.TITLE = self.val()
        self.AUTHOR = 'Dmitry Ponyatov'
        self.EMAIL = 'dponyatov@gmail.com'
        self.YEAR = 2020
        self.LICENSE = 'All rights reserved'
        self.COPYRIGHT = f'(c) {self.AUTHOR} <<{self.EMAIL}>> {self.YEAR} {self.LICENSE}'
        self.GITHUB = f'https://github.com/ponyatov/{self}'

    def readme(self):
        self.readme = readmeFile(); self.d // self.readme

    def doxy(self):
        self.doxy = doxyFile(); self.d // self.doxy

    def py(self):
        self.py = pyFile(self.val()); self.d // self.py

    def vscode(self):
        self.vscode = Dir('.vscode'); self.d // self.vscode
        self.settings()
        self.tasks()
        self.extensions()

    def tasks(self):
        self.vscode.tasks = jsonFile('tasks')
        self.vscode // self.vscode.tasks

    def extensions(self):
        self.vscode.extensions = jsonFile('extensions')
        self.vscode // self.vscode.extensions

    def settings(self):
        self.settings = jsonFile('settings') // S('{', '}')
        self.vscode // self.settings

        def multi(key, cmd):
            return (S('{', '},')
                    // f'"command": "multiCommand.{key}",'
                    // (S('"sequence": [', ']')
                        // '"workbench.action.files.saveAll",'
                        // (S('{"command": "workbench.action.terminal.sendSequence",')
                            // f'"args": {{"text": "\\u000D clear ; LANG=C {cmd} \\u000D"}}}}')
                        )
                    )
        self.settings[0] \
            // (Sec('multi')
                // (S('"multiCommand.commands": [', '],')
                    // multi('f12', 'make all')))
        #
        self.exclude = (S('"files.exclude": {', '},')
                        // f'"**/docs/**":true,'
                        // f'"**/{self}/**":true,')
        self.watcher = (S('"files.watcherExclude": {', '},')
                        // f'"**/docs/**":true,'
                        // f'"**/{self}/**":true,')
        self.assoc = S('"files.associations": {', '},')
        self.settings[0] // (Sec('files', pfx='')
                             // self.exclude
                             // self.watcher
                             // self.assoc)
        #
        self.settings[0] // (Sec('editor', pfx='')
                             // '"editor.tabSize": 4,'
                             // '"editor.rulers": [80],'
                             // '"workbench.tree.indent": 32,')
        #
        self.settings[0] // Sec('msys', pfx='')

    def giti(self):
        self.d.giti = gitiFile(); self.d // self.d.giti
        self.d.giti.top // '*~' // '*.swp' // '*.log'
        self.d.giti // (Sec(pfx='', sfx='') // f'/{self}/' // '/docs/')

    def dirs(self):
        self.d = Dir(self.value); self.giti()
        #
        self.bin = Dir('bin'); self.d // self.bin
        self.bin.giti = gitiFile(); self.bin // (self.bin.giti // '*')
        #
        self.doc = Dir('doc'); self.d // self.doc
        self.doc.giti = gitiFile(); self.doc \
            // (self.doc.giti // '*.pdf' // '*.djvu')
        #
        self.lib = Dir('lib'); self.d // self.lib
        self.lib.giti = gitiFile(); self.lib // self.lib.giti
        #
        self.src = Dir('src'); self.d // self.src
        self.src.giti = gitiFile(); self.src \
            // (self.src.giti // '*-*/')
        #
        self.tmp = Dir('tmp'); self.d // self.tmp
        self.tmp.giti = gitiFile(); self.tmp // (self.tmp.giti // '*')

    def mk(self):
        self.mk = mkFile(); self.d // self.mk
        #
        self.mk.var = Sec('var'); self.mk // self.mk.var
        (self.mk.var
         // 'MODULE  = $(notdir $(CURDIR))'
         // 'OS      = $(shell uname -o|tr / _)'
         // 'NOW     = $(shell date +%d%m%y)'
         // 'REL     = $(shell git rev-parse --short=4 HEAD)'
         // 'BRANCH  = $(shell git rev-parse --abbrev-ref HEAD)'
         // 'PEPS    = --ignore=E265,E302,E401,E402,E702')
        #
        self.mk.tool = Sec('tool', pfx=''); self.mk // self.mk.tool
        (self.mk.tool
         // 'CURL = curl -L -o'
         // 'CF   = clang-format-11 -style=file -i'
         // 'PY   = $(shell which python3)'
         // 'PIP  = $(shell which pip3)'
         // 'PEP  = $(shell which autopep8)')
        #
        self.mk.src = Sec('src', pfx=''); self.mk // self.mk.src
        (self.mk.src
         // 'Y += $(MODULE).py'
         // 'S += $(Y)')
        #
        self.mk.cfg = Sec('cfg', pfx=''); self.mk // self.mk.cfg
        #
        self.mk.bin = Sec('bin', pfx=''); self.mk // self.mk.bin
        #
        self.mk.all = Sec('all', pfx=''); self.mk // self.mk.all
        (self.mk.all
            // (S('all: $(PY) $(MODULE).py')
                // '$^ $@ && $(MAKE) tmp/format_py'))
        #
        self.mk.format = Sec('format', pfx=''); self.mk // self.mk.format
        (self.mk.format
            // (S('tmp/format_py: $(Y)')
                // '$(PEP) $(PEPS) -i $? && touch $@'))
        #
        self.mk.rule = Sec('rule', pfx=''); self.mk // self.mk.rule
        #
        self.mk.doc = Sec('doc', pfx=''); self.mk // self.mk.doc
        #
        self.mk.install = Sec('install', pfx=''); self.mk // self.mk.install
        #
        self.mk.merge = Sec('merge', pfx=''); self.mk // self.mk.merge

    def cf(self):
        self.cf = File('', '.clang-format'); self.d // self.cf
        (self.cf
         // '# https://clang.llvm.org/docs/ClangFormatStyleOptions.html'
         // ''
         // 'BasedOnStyle: Google'
         // 'IndentWidth: 4'
         // 'ColumnLimit: 80'
         // ''
         // 'SortIncludes: false'
         // ''
         // 'AllowShortBlocksOnASingleLine: Always'
         // 'AllowShortFunctionsOnASingleLine: All'''
         // ''
         // 'Language: Cpp'
         // ''
         // '# Language: JavaScript')

    def apt(self):
        self.apt = File('apt', '.txt'); self.d // self.apt
        (self.apt
            // 'git make curl'
            // 'python3 python3-venv python3-pip'
            // 'code meld doxygen')

    def reqs(self):
        self.reqs = File('requirements', '.txt'); self.d // self.reqs

    def sync(self): self.d.sync()


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'all':
            p = Project()
            p.TITLE = 'Object / Stack Language'
            p.sync()
        else:
            raise TypeError(['sys.argv', sys.argv])
    except IndexError:
        pass
