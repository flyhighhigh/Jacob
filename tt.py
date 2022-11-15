import git

print('')
g = git.cmd.Git()
ret = g.add(".")
print("ret",ret)
print(g.status())
g.commit("-m","auto commit by GitPython (reports.json)")
print('')