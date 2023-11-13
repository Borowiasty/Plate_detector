from pathlib import Path

for p in Path('.').glob('**/dataset_3/**/*.txt'):
    content = p.read_text()
    if content != '':
        if content[0] == '1':
            while(content.find('1 ') != -1):
                if(content.find('1 ') == 0):
                    content = '0' + content[1:]
                else:
                    content = content[:content.find('1 ')-1] + '\n0' + content[content.find('1 ')+1:]

            file = p.open('w')
            file.write(content)
print("FINISHED")
