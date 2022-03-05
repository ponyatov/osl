import os,sys

class Object:
    def __init__(self,V):
        self.value = V

class IO(Object): pass

class Dir(IO): pass

class File(IO): pass

class Meta(Object): pass

class Project(Meta):
    def __init__(self,V):
        super().__init__(V)

p = Project()
p.sync()


# for d in '.vscode bin doc lib src tmp'.split():
#     try: os.mkdir(d)
#     except: pass
#     open(f'{d}/.gitignore','w')

# with open('apt.txt','w') as apt:
#     apt.write('''git make curl
# python3 python3-venv python3-pip
# ''')

# reqs = open('requirements.txt','w')

# with open('Makefile','w') as mk:
#     install update:
#         sudo apt update
#         sudo apt install -u `cat apt.txt`


# cf = open('.clang-format','w')

# readme = open('README.md','w')
