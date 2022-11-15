import git

g = git.cmd.Git()
ret = g.add(".")
ret:str = g.status()
ret = ret[ret.find("Changes to be committed:"):]
ret = ret.split('\n')[2:-1]
modified = ''
for i in ret:
    modified += i[i.find(':')+1:].replace(' ','')+' '
g.commit("-m",f"auto commit by GitPython ({modified})")
ret = g.push()