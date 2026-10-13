"""Faithful Chinese names and explicitly approximate exterior form choices."""
GIS='https://gis.maps.uw.edu/federated/rest/services/BaseComponents/UW_Seattle_Buildings_and_Paths/MapServer/1'
MAP='https://map.uw.edu/?id=2099'
# These heights describe public-source exterior approximations, not a survey.
LANDMARKS=['SUZ','GRB','DEN','MGH','SAV','RAI','SMI','GWN','KNE','OUG','HUB','BRK','HAG','PCAR','LAW','CSE','CSE2','LSB','HRC','HSEB','UMSA','STD','EDP','CSH','INT','IEB']
GOTHIC={'SUZ','GRB','MGH','SAV','RAI','SMI','GWN','MLR','MUS','HUT','THO','HNS','JHN','GUG','AND','ROB'}
PITCHED=GOTHIC|{'DEN','LEW','CLK','ARC','OBS','HPT','INT','EDP','PHT'}
HEIGHTS={'SUZ':32.5,'GRB':35,'DEN':26,'MGH':27,'SAV':23,'RAI':21,'SMI':23,'GWN':23,'MLR':21,'HNS':25,'MCM':36,'KNE':16,'OUG':16,'HUB':21,'BRK':15,'PCAR':22,'LAW':20,'CSE':27,'CSE2':30,'LSB':32,'HRC':33,'HSEB':21,'IEB':28,'UMSA':39,'STD':41,'EDP':26,'CSH':14,'INT':11,'UWT':99,'UWTC':99,'HST':46,'HND':30,'HSH':28,'HSK':32,'PAT':28,'PAB':26,'PAA':15}
REFS={'SUZ':'https://lib.uw.edu/locations-hours/suzzallo-and-allen-libraries-history/','DEN':'https://pcad.lib.washington.edu/building/5433/','STD':'https://gohuskies.com/sports/2013/7/2/208568068','IEB':'https://www.engr.washington.edu/about/facilities','INT':'https://www.washington.edu/diversity/tribal-relations/intellectual-house/','BRK':'https://www.burkemuseum.org/','CSH':'https://gohuskies.com/facilities/conibear-shellhouse/9'}
ZH={'CNH':'ASUW学生会赛艇艇库'}
for line in '''
ICT|族裔文化中心剧场
IC2|教学中心附楼
MEB|机械工程楼
EGA|工程附楼
CSE|保罗·G·艾伦计算机科学与工程中心
WNX|温肯韦德附楼
RAI|雷特楼
KIR|柯斯滕风洞实验楼
SMI|史密斯楼
ART|艺术楼
AER|航空航天与工程研究楼
ACC|约翰·M·华莱士楼
WCL|威尔逊陶瓷实验室
WIL|威尔科克斯楼
CSH|科尼贝尔赛艇艇库
ADL|空气动力学实验室
NHS|西北园艺学会会馆
ISA|艾萨克森楼
NMH|梅里尔楼
PHT|弗洛伊德与德洛丽丝·琼斯剧院
CLK|克拉克楼
RAX|罗伯茨附楼
ESB|环境安全储藏楼
DRC|道格拉斯研究温室
SSB|布鲁克林步道楼
HND|亨德森楼
CDH|康登楼
NLB|北湖楼
CDA|Commodore-Duchess 公寓
GAB|格雷夫斯附楼
ESO|环境安全办公楼
CHSB|人类发展与残障研究所南楼
OTB|海洋学教学楼
OCE|海洋学楼
MSB|海洋科学楼
HCK|希区柯克楼
WLA|威尔逊附楼
ODB|海洋学码头楼
MAR|海洋研究楼
HSK|菲亚尔科生物医学研究楼（K翼）
ICH|坎宁安楼
HHL|哈里斯水力学实验室
OSS|海洋学储藏棚
ROB|罗伯茨楼
BAG|巴格利楼
SIG|西格楼
LOW|洛楼
PWR|动力站
UMSP|华盛顿大学蒙特莱克医疗中心 · 外科与治疗楼
BIOE|威廉·H·福格生物工程楼
GNOM|威廉·H·福格基因组科学楼
RTB|本杰明楼 · 跨学科研究
ECE|电气与计算机工程楼
ALB|艾伦图书馆
SMZ|施密茨楼
TGB|格雷夫斯楼
WFS|温肯韦德森林科学实验室
IMA|校园文体活动中心
ELM|榆树宿舍楼
MLR|米勒楼
PSB|设施服务楼
NPS|北物理实验室 · 回旋加速器工坊
SHA|艇库附楼
EXED|美国银行高管教育中心
MOL|分子工程与科学楼
LAW|威廉·H·盖茨楼
MUS|音乐楼
PAT|物理与天文学塔楼
STD|哈士奇体育场
BSG|棒球场看台
CDRE|雪松东公寓
CDRW|雪松西公寓
DEM|登普西楼
CHCL|人类发展与残障研究所诊所
ELB|工程图书馆
OR2|海洋研究二号楼
EGL|伊格尔森楼
FAC|华盛顿大学俱乐部（教职工中心）
PCAR|帕卡尔楼
NPC|北物理实验室 · 回旋加速器楼
GUA|古根海姆附楼
URC|西南维护楼
UHF|城市园艺场务楼
TSB|交通服务楼
GWN|高文楼
CCC|儿童托育中心
WAC|水上活动中心
FSB|车队服务楼
BNS|本森楼
SUZ|苏扎洛图书馆
HUB|哈士奇学生会馆
UMSA|华盛顿大学蒙特莱克医疗中心 · 蒙特莱克塔楼（SA翼）
SBS|哈士奇垒球场
ECC|塞缪尔·E·凯利族裔文化中心
LAN|兰德宿舍楼
BLD|布洛德尔楼
ATG|大气科学与地球物理楼
SPG|南校区停车楼
INT|Intellectual House（原住民文化交流中心）
FLK|弗卢克楼
HLL|戴维·C·霍尔楼
JHN|约翰逊楼
MGH|玛丽·盖茨楼
GUG|古根海姆楼
CHB|化学楼
AND|安德森楼
MOR|莫尔楼
KIN|金凯德楼
PAA|物理与天文学礼堂
PAB|物理与天文学楼
GTH|格思里楼
ARC|建筑学楼
GRB|格伯丁楼
MNY|米尼礼堂
OUG|奥德加德本科图书馆
KNE|凯恩楼
PAR|帕林顿楼
HAG|亨利美术馆
AVA|费伊·G·艾伦视觉艺术中心
PDL|帕德尔福德楼
THO|汤姆森楼
CMU|传播学楼
MCM|麦克马洪宿舍楼
NPV|北物理实验室 · 范德格拉夫加速器楼
HNS|汉西宿舍楼
HPT|格伦·休斯顶层剧场
LEW|刘易斯楼
HUT|哈钦森楼
SAV|萨弗里楼
DEN|丹尼楼
OBS|西奥多·雅各布森天文台
SWS|社会工作、言语与听力科学楼
POP|杨树宿舍楼
ALD|桤木宿舍楼
GLD|古尔德楼
WRS|西受电站
PSV|出版服务楼
CMA|陶瓷与金属艺术楼
GDR|高尔夫练习场楼
FSH|渔业科学楼
FTR|渔业教学与研究楼
WCP|波蒂奇湾停车楼（西校区停车楼）
OCN|海洋科学楼
SOCC|南校区中心
PBB|波蒂奇湾楼
CHSC|哈林中心 · EEU学校
IPF|登普西室内训练中心
NTC|诺德斯特龙网球中心
EDP|赫克·埃德蒙森体育馆
MAH|枫树宿舍楼
TEH|特里宿舍楼
UWPD|华盛顿大学警察局
POB|设施运营楼
WCUP|西校区公用设施站
NAN|纳米工程与科学楼
LSB|生命科学楼
LSG|生命科学温室
CSE2|比尔与梅琳达·盖茨计算机科学与工程中心
WLW|马文·奥利弗宿舍楼
MCC|麦卡蒂宿舍楼
MDR|撒迪厄斯与洛伊丝·斯普拉特伦宿舍楼
BRK|伯克自然历史与文化博物馆
ERS|东受电站
UMPH|华盛顿大学蒙特莱克医疗中心 · 泵房
HRC|汉斯·罗斯林人口健康中心
OAK|橡树宿舍楼
UMCW|华盛顿大学蒙特莱克医疗中心 · 冷冻水站
FNDR|创始人楼
SBPC|垒球训练中心
HSEB|健康科学教育楼
IEB|跨学科工程楼
BOHC|篮球训练中心
UWTC|华盛顿大学塔楼 · C楼
UWTO|华盛顿大学塔楼 · O楼
UWTT|华盛顿大学塔楼 · T楼
UWTS|华盛顿大学塔楼 · S楼
UWT|华盛顿大学塔楼
'''.strip().splitlines():
    code,name=line.split('|');ZH[code]=name
SHORT={'SUZ':'Suzzallo Library','GRB':'Gerberding Hall','DEN':'Denny Hall','MGH':'Mary Gates Hall','STD':'Husky Stadium','EDP':'Hec Edmundson Pavilion','HUB':'Husky Union Building','OUG':'Odegaard Library','BRK':'Burke Museum','HRC':'Rosling Center','LAW':'Gates Hall','CSE':'Allen Center','CSE2':'Gates Center','IEB':'Interdisciplinary Engineering','UMSA':'UW Medical Center','INT':'Intellectual House'}
def chinese(code,en):
    if code in ZH:return ZH[code]
    if code.startswith('HS'):return '马格努森健康科学中心 · '+code[2:]+'翼'
    if code.startswith('UM'):return '华盛顿大学蒙特莱克医疗中心 · '+code[2:]+'翼'
    if code.startswith('CY'):return '设施场区 · '+code[2:]+'号集装箱设施' if code!='CYCO' else '设施场区集装箱办公室'
    if code.startswith('GH'):return '校园门岗 '+code[2:]
    if code.startswith('PO'):return '设施运营附楼 '+code[2:]
    if code.startswith('SC') and len(code)==3:return '史蒂文斯庭院宿舍 · '+code[2]+'楼'
    if code.startswith('MRC'):return '默瑟庭院宿舍 · '+code[3:]+'楼'
    if code.startswith('NC'):return '诺德海姆庭院宿舍 · '+code[2:]+'楼'
    if code.startswith('TL'):return '劳雷尔村儿童中心 · 模块设施 '+code[2:]
    if en[0].isdigit():
        return en.replace('University Way NE','东北大学路').replace('Brooklyn Ave NE','东北布鲁克林大道').replace('NE Boat St','东北船街').replace('NE Northlake Way','东北北湖路')+'号楼'
    return en+'（校园设施）'
