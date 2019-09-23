from common_crawler import *

replace_list = ['\r', '\t', '\u3000', '&nbsp;', '&quot;', '&#8221;', '&lt;', '&gt;', '&#183;']
strip_list = [' ', '\\']  # only replace characters at the line's beginning and ending

# url = 'http://music.yule.sohu.com/20091109/n268066205.shtml'
# url = 'http://ent.qq.com/a/20091109/000253.htm'  #  连接多
# url = 'https://kexue.fm/'     # 格式独特
# url = 'https://kexue.fm/archives/5776'
# url = 'https://blog.csdn.net/ying86615791/article/details/76215363'  # 内容分散
# url = 'https://www.2cto.com/kf/201703/611583.html'    # 正文少
# url = 'http://www.cnblogs.com/blueel/archive/2013/01/14/2859497.html'
# url = 'https://blog.csdn.net/singwhatiwanna/article/details/48439621'   # 正文篇章多
url = 'https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/#id17'      # 文档类型

sess = requests.Session()
html = sess.get(url)

encoding = re.findall('charset=["]*([^\s";]+)', html.text)  # get html encoding automatically
html.encoding = encoding[0]
match = re.sub(r'(?is)<pre.*?</pre>|'
               r'(?is)<style.*?</style>|'
               r'(?is)<script.*?</script>|'
               r'(?is)<!--.*?-->|'
               r'(?is)<.*?>|'
               r'(?is)<head.*?</head>|',
               '',
               html.text)  # sub areas of pre, style, script, label comment, labels

sub = re.sub(u'(?is)<.*?>', '', match)
for i in replace_list:
    sub = sub.replace(i, '')
sub_list = sub.split('\n')
for i in range(len(sub_list)):
    for j in strip_list:
        sub_list[i] = sub_list[i].strip(j)
print(sub_list)
soup = BeautifulSoup(match, 'lxml')

q = []
s = []
q.append(soup.body)
while len(q) != 0:
    node = q.pop(0)
    try:
        for i in node.children:
            q.append(i)
    except AttributeError:
        if node.string == '\n':
            pass
        else:
            if node.parent.string is not None:
                s.append(node)

d = {}
for i, n in enumerate(s):
    d[n.parent.name] = d.get(n.parent.name, [])
    sen = n.string
    for r in replace_list:
        sen = sen.replace(r, '')
    sen = sen.replace('\n', '')
    for r in strip_list:
        sen = sen.strip(r)
    try:
        ind = sub_list.index(sen)
    except ValueError:
        for j, a in enumerate(sub_list):
            if sen in a:
                ind = j
    try:
        d[n.parent.name].append(ind)
    except:
        d[n.parent.name].append(-1)

count = []
for i in sub_list:
    words = re.findall(u'[a-zA-Z]*', i)
    count.append(len(i) - len(words) / 2)

kc = 4
c = []
for i in range(kc, len(count) - kc - 1):
    c.append(sum(count[i - kc:i + kc + 1]) / 5.)

line = {}
cl = {}
j = 0
flag = 0
for i in range(kc, len(count) - kc - 1):
    if flag == 0 and count[i] > 7 and c[i - kc] > 10:
        flag = 1
    if flag == 1:
        line[j] = line.get(j, [])
        cl[j] = cl.get(j, [])
        line[j].append(i)
        for k, v in d.items():
            if i in v:
                cl[j].append(k)
    if flag == 1 and count[i] < 4 and c[i - kc] < 10:
        flag = 0
        j += 1

o = {}
for k, v in cl.items():
    se = set(v)
    maxv = -1
    maxk = ''
    for i in se:
        a = v.count(i)
        if a > maxv:
            maxv = a
            maxk = i
    o[k] = maxk

print(cl)
print(o)
flag = 1
a = o[0]
i = line[0][0]
for k, v in line.items():
    if a == '':
        a = '_'
    b = o[k]
    if a != b:
        flag = 1
    else:
        flag = 0
    if flag == 1:
        for _ in range(i, j):
            if count[_] > 5:
                print(sub_list[_])
        print('\n###################')
        i = v[0]
    a = b
    j = v[-1]


for _ in range(i, j):
    if count[_] > 5:
        print(sub_list[_])
print('\n###################')
