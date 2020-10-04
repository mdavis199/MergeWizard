@set moprofiles=G:\ModTools\ModOrganizer\profiles\
@set zeditprofile=G:\ModTools\zEdit\profiles\Skyrim SE
@robocopy "%~dp0\testdata\MYTEST" "%moprofiles%\MYTEST" /NFL /NDL /NJH /NJS
@robocopy "%~dp0\testdata" "%zeditprofile%" merges.json /NFL /NDL /NJH /NJS