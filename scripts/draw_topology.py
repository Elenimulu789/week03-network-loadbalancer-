"""Recreate the supplied diagram; optional dependency: Pillow (pip install pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
image = Image.new('RGB', (1400, 1060), '#f3f6fa')
draw = ImageDraw.Draw(image)
font_dir = Path('/usr/share/fonts/truetype/dejavu')
def font(size, bold=False):
    filename = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    try:
        return ImageFont.truetype(str(font_dir / filename) if font_dir.exists() else filename, size)
    except OSError:
        return ImageFont.load_default(size=size)
def text(x,y,value,size=23,fill='#1a334c',bold=False):
    draw.text((x,y),value,font=font(size,bold),fill=fill)
def center(x,y,value,size=23,fill='#1a334c',bold=False):
    f=font(size,bold)
    box=draw.textbbox((0,0),value,font=f)
    draw.text((x-(box[2]-box[0])/2,y),value,font=f,fill=fill)
def box(rect,fill,outline='#d4dfeb',radius=22,width=2):
    draw.rounded_rectangle(rect,radius=radius,fill=fill,outline=outline,width=width)
def arrow(points,fill='#557b9b'):
    draw.line(points,fill=fill,width=5,joint='curve')
    x,y=points[-1]
    draw.polygon([(x,y),(x-9,y-15),(x+9,y-15)],fill=fill)

text(65,35,'WEEK 03 / NETWORK TOPOLOGY',19,'#47718c',True)
text(65,72,'One public gateway. Two private backends.',39,bold=True)
text(65,129,'Local Docker Compose lab | Layer 7 HTTP | Default round-robin',23,'#596f84')
box((440,185,960,275),'white')
center(700,207,'Browser / host client',25,bold=True)
center(700,243,'127.0.0.1:8080',20)
box((65,320,1335,535),'#e5effa','#b8cee6')
text(95,342,'PUBLIC SUBNET',22,'#38648c',True)
text(95,379,'172.28.40.0/24',20)
text(95,414,'Normal ingress',18,'#596f84')
box((65,575,1335,930),'#e5f1eb','#b4d4c4')
text(95,599,'PRIVATE SUBNET',22,'#31694f',True)
text(95,636,'172.28.41.0/24',20)
text(95,670,'internal: true',19,'#31694f')
arrow([(700,275),(700,405)])
box((445,405,955,685),'#183b59','#183b59')
center(700,429,'NGINX LOAD BALANCER',25,'white',True)
center(700,473,'Public + private interfaces',21,'#d7e8f4')
center(700,513,'Container port 80',21,'#d7e8f4')
center(700,555,'Round-robin + bounded retries',20,'#d7e8f4')
center(700,607,'Only service publishing a host port',18,'#b9d9ec')
arrow([(620,685),(620,724),(460,724),(460,770)],'#44795d')
arrow([(780,685),(780,724),(1030,724),(1030,770)],'#44795d')
box((260,770,655,890),'white','#afd0bf')
box((830,770,1225,890),'white','#afd0bf')
center(457,789,'backend_1',28,bold=True)
center(457,836,'Port 3000 | no host mapping',19)
center(1027,789,'backend_2',28,bold=True)
center(1027,836,'Port 3000 | no host mapping',19)
text(75,955,'Traffic: client → Nginx → one backend → client',23,bold=True)
text(75,996,'Boundary: ordinary clients and public-side containers. Docker host administrators remain trusted.',18,'#596f84')
output=ROOT/'docs/network-topology.png'
image.save(output)
print(output)
