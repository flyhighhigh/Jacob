import git

print('')
g = git.cmd.Git()
ret = g.add(".")
print("ret",ret)
g.commit("-m","auto commit by GitPython (reports.json)")
print('')