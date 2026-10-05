import pygame, random, math, sys

pygame.init()
W,H=1100,700
WORLD_W,WORLD_H=3000,2200
screen=pygame.display.set_mode((W,H))
pygame.display.set_caption("Battle Arena")
clock=pygame.time.Clock()
FONT=pygame.font.SysFont("arial",22)
SMALL=pygame.font.SysFont("arial",16)
BIG=pygame.font.SysFont("arial",52,bold=True)
TITLE=pygame.font.SysFont("arial",68,bold=True)

WHITE=(245,245,245); BLACK=(15,18,20); DARK=(28,34,38)
GRASS=(70,145,70); GRASS2=(78,154,76); ROAD=(105,105,105)
RED=(225,55,55); BLUE=(55,125,235); YELLOW=(245,205,50)
ORANGE=(245,130,40); PURPLE=(155,80,215); GREEN=(60,210,100)
CYAN=(60,205,220); BROWN=(130,90,55)

def clamp(v,a,b): return max(a,min(b,v))
def dist(a,b,c,d): return math.hypot(a-c,b-d)
def w2s(x,y,cx,cy): return int(x-cx),int(y-cy)

class Bullet:
    def __init__(self,x,y,vx,vy,owner):
        self.x,self.y,self.vx,self.vy=x,y,vx,vy
        self.owner=owner; self.damage=32 if owner=="player" else 10
        self.life=1.4; self.radius=4
    def update(self,dt):
        self.x+=self.vx*dt; self.y+=self.vy*dt; self.life-=dt

class Pickup:
    def __init__(self,x,y,kind):
        self.x,self.y,self.kind=x,y,kind; self.radius=14

class Player:
    def __init__(self):
        self.x,self.y=WORLD_W/2,WORLD_H/2
        self.radius=20; self.speed=275
        self.health=self.max_health=100
        self.magazine=self.max_magazine=30
        self.reserve_ammo=120; self.reload_time=1.5
        self.reload_timer=0; self.fire_delay=.14; self.fire_timer=0
        self.medkits=2; self.kills=0; self.angle=0
    def update(self,dt):
        k=pygame.key.get_pressed()
        dx=(k[pygame.K_d] or k[pygame.K_RIGHT])-(k[pygame.K_a] or k[pygame.K_LEFT])
        dy=(k[pygame.K_s] or k[pygame.K_DOWN])-(k[pygame.K_w] or k[pygame.K_UP])
        if dx or dy:
            n=math.hypot(dx,dy); dx/=n; dy/=n
            self.x+=dx*self.speed*dt; self.y+=dy*self.speed*dt
        self.x=clamp(self.x,self.radius,WORLD_W-self.radius)
        self.y=clamp(self.y,self.radius,WORLD_H-self.radius)
        self.fire_timer=max(0,self.fire_timer-dt)
        if self.reload_timer>0:
            self.reload_timer-=dt
            if self.reload_timer<=0:
                need=self.max_magazine-self.magazine
                take=min(need,self.reserve_ammo)
                self.magazine+=take; self.reserve_ammo-=take
    def reload(self):
        if self.reload_timer<=0 and self.magazine<self.max_magazine and self.reserve_ammo:
            self.reload_timer=self.reload_time
    def heal(self):
        if self.medkits and self.health<self.max_health:
            self.health=min(self.max_health,self.health+45); self.medkits-=1
    def shoot(self,tx,ty):
        if self.reload_timer>0 or self.fire_timer>0: return None
        if self.magazine<=0: self.reload(); return None
        dx,dy=tx-self.x,ty-self.y; n=math.hypot(dx,dy) or 1
        dx/=n; dy/=n; self.angle=math.atan2(dy,dx)
        self.fire_timer=self.fire_delay; self.magazine-=1
        return Bullet(self.x+dx*25,self.y+dy*25,dx*1000,dy*1000,"player")

class Enemy:
    def __init__(self,p):
        self.radius=18; self.health=100; self.speed=random.randint(75,120)
        self.shoot_timer=random.uniform(.7,2); self.angle=0
        while True:
            self.x=random.randint(100,WORLD_W-100); self.y=random.randint(100,WORLD_H-100)
            if dist(self.x,self.y,p.x,p.y)>550: break
    def update(self,dt,p):
        d=dist(self.x,self.y,p.x,p.y)
        if d<800:
            dx,dy=p.x-self.x,p.y-self.y; n=math.hypot(dx,dy) or 1
            self.angle=math.atan2(dy,dx)
            if d>260:
                self.x+=dx/n*self.speed*dt; self.y+=dy/n*self.speed*dt
            self.shoot_timer-=dt
            if self.shoot_timer<=0 and d<650:
                self.shoot_timer=random.uniform(1,1.8)
                return Bullet(self.x,self.y,dx/n*600,dy/n*600,"enemy")
        self.x=clamp(self.x,self.radius,WORLD_W-self.radius)
        self.y=clamp(self.y,self.radius,WORLD_H-self.radius)
        return None

class Zone:
    def __init__(self):
        self.x,self.y=WORLD_W/2,WORLD_H/2
        self.radius=self.target=1000; self.timer=30; self.phase=0
    def update(self,dt):
        self.timer-=dt
        if self.timer<=0 and self.radius>260:
            self.timer=25; self.target=max(260,self.radius-160); self.phase+=1
        if self.radius>self.target:
            self.radius=max(self.target,self.radius-10*dt)
    def outside(self,x,y): return dist(x,y,self.x,self.y)>self.radius

def make_world():
    buildings=[]; trees=[]
    for _ in range(28):
        w=random.randint(90,190); h=random.randint(70,150)
        x=random.randint(100,WORLD_W-w-100); y=random.randint(100,WORLD_H-h-100)
        if dist(x+w/2,y+h/2,WORLD_W/2,WORLD_H/2)>300:
            buildings.append(pygame.Rect(x,y,w,h))
    for _ in range(170):
        x=random.randint(50,WORLD_W-50); y=random.randint(50,WORLD_H-50)
        if not any(b.inflate(50,50).collidepoint(x,y) for b in buildings):
            trees.append((x,y,random.randint(16,24)))
    return buildings,trees

def text(s,x,y,font=FONT,color=WHITE,center=False):
    r=font.render(s,True,color).get_rect()
    r.center=(x,y) if center else r.center
    if not center: r.topleft=(x,y)
    screen.blit(font.render(s,True,color),r)

def draw_world(cx,cy,buildings,trees):
    screen.fill(GRASS)
    for x in range(int(cx//80)*80,int(cx+W)+80,80):
        pygame.draw.line(screen,GRASS2,(x-int(cx),0),(x-int(cx),H))
    for y in range(int(cy//80)*80,int(cy+H)+80,80):
        pygame.draw.line(screen,GRASS2,(0,y-int(cy)),(W,y-int(cy)))
    ry=int(WORLD_H*.28-cy); rx=int(WORLD_W*.70-cx)
    pygame.draw.rect(screen,(75,75,75),(0,ry-34,W,68)); pygame.draw.rect(screen,ROAD,(0,ry-28,W,56))
    pygame.draw.rect(screen,(75,75,75),(rx-34,0,68,H)); pygame.draw.rect(screen,ROAD,(rx-28,0,56,H))
    for x in range(-100,W+100,70): pygame.draw.rect(screen,YELLOW,(x,ry-2,35,4))
    for y in range(-100,H+100,70): pygame.draw.rect(screen,YELLOW,(rx-2,y,4,35))
    for x,y,r in trees:
        sx,sy=w2s(x,y,cx,cy)
        if -50<sx<W+50 and -50<sy<H+50:
            pygame.draw.rect(screen,BROWN,(sx-4,sy+5,8,18))
            pygame.draw.circle(screen,(35,105,45),(sx,sy),r)
            pygame.draw.circle(screen,(45,125,52),(sx-6,sy-5),r//2)
    for b in buildings:
        r=pygame.Rect(int(b.x-cx),int(b.y-cy),b.width,b.height)
        if r.right<0 or r.left>W or r.bottom<0 or r.top>H: continue
        pygame.draw.rect(screen,(60,65,72),r); pygame.draw.rect(screen,(35,38,43),r,4)
        for wx in range(r.left+18,r.right-10,35):
            for wy in range(r.top+18,r.bottom-10,35):
                pygame.draw.rect(screen,(225,190,85),(wx,wy,13,13))

def draw_player(p,cx,cy):
    sx,sy=w2s(p.x,p.y,cx,cy)
    pygame.draw.ellipse(screen,(40,80,40),(sx-23,sy+12,46,14))
    pygame.draw.circle(screen,BLUE,(sx,sy),p.radius); pygame.draw.circle(screen,(25,70,150),(sx,sy),p.radius,3)
    hx=sx+int(math.cos(p.angle)*9); hy=sy+int(math.sin(p.angle)*9)
    pygame.draw.circle(screen,(235,185,145),(hx,hy-5),8)
    gx=sx+int(math.cos(p.angle)*32); gy=sy+int(math.sin(p.angle)*32)
    pygame.draw.line(screen,BLACK,(sx,sy),(gx,gy),8)

def draw_enemy(e,cx,cy):
    sx,sy=w2s(e.x,e.y,cx,cy)
    pygame.draw.ellipse(screen,(45,70,45),(sx-21,sy+12,42,12))
    pygame.draw.circle(screen,RED,(sx,sy),e.radius); pygame.draw.circle(screen,(130,25,25),(sx,sy),e.radius,3)
    pygame.draw.circle(screen,(225,175,135),(sx,sy-7),7)
    gx=sx+int(math.cos(e.angle)*28); gy=sy+int(math.sin(e.angle)*28)
    pygame.draw.line(screen,BLACK,(sx,sy),(gx,gy),7)
    pygame.draw.rect(screen,BLACK,(sx-24,sy-36,48,7))
    pygame.draw.rect(screen,GREEN,(sx-24,sy-36,int(48*max(0,e.health)/100),7))

def draw_pickup(i,cx,cy):
    sx,sy=w2s(i.x,i.y,cx,cy)
    if i.kind=="ammo":
        pygame.draw.rect(screen,YELLOW,(sx-11,sy-13,22,26)); text("A",sx,sy,SMALL,BLACK,True)
    else:
        pygame.draw.rect(screen,WHITE,(sx-13,sy-13,26,26))
        pygame.draw.rect(screen,RED,(sx-4,sy-10,8,20)); pygame.draw.rect(screen,RED,(sx-10,sy-4,20,8))

def draw_hud(p,enemies,z):
    pygame.draw.rect(screen,BLACK,(20,20,250,28))
    pygame.draw.rect(screen,GREEN if p.health>35 else RED,(24,24,int(242*p.health/100),20))
    text(f"HP {max(0,int(p.health))}",30,22,SMALL)
    text(f"AMMO {p.magazine}/{p.reserve_ammo}",20,58)
    if p.reload_timer>0: text("RELOADING...",20,88,SMALL,YELLOW)
    text(f"MEDKITS {p.medkits}",20,108,SMALL); text(f"KILLS {p.kills}",20,132,SMALL)
    text(f"PLAYERS LEFT: {len(enemies)+1}",W-220,20,SMALL)
    text(f"ZONE: {int(z.radius)}",W-220,46,SMALL); text(f"NEXT SHRINK: {max(0,int(z.timer))}s",W-220,70,SMALL)
    pygame.draw.rect(screen,(0,0,0,130),(W-275,H-88,255,68))
    text("WASD = Move | Mouse = Aim/Shoot",W-265,H-78,SMALL)
    text("R = Reload | E = Medkit | P = Pause",W-265,H-53,SMALL)

def draw_zone(z,cx,cy):
    sx,sy=w2s(z.x,z.y,cx,cy)
    overlay=pygame.Surface((W,H),pygame.SRCALPHA); overlay.fill((110,40,180,80))
    pygame.draw.circle(overlay,(0,0,0,0),(sx,sy),int(z.radius))
    screen.blit(overlay,(0,0)); pygame.draw.circle(screen,(180,80,240),(sx,sy),int(z.radius),4)

def menu():
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_RETURN: return
                if e.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
        screen.fill((20,30,45))
        text("BATTLE",W//2,190,TITLE,YELLOW,True); text("ARENA",W//2,260,TITLE,RED,True)
        text("2D Battle Royale",W//2,330,BIG,WHITE,True)
        text("ENTER - START GAME",W//2,430,FONT,CYAN,True)
        text("WASD / ARROWS to move • Mouse to aim • Left click to shoot",W//2,475,SMALL,WHITE,True)
        text("Survive the shrinking zone and eliminate the bots!",W//2,505,SMALL,WHITE,True)
        text("ESC - Quit",W//2,570,SMALL,(180,180,180),True)
        pygame.display.flip(); clock.tick(60)

def game_over(win,p):
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_RETURN: return True
                if e.key==pygame.K_ESCAPE: return False
        screen.fill(DARK)
        text("VICTORY!" if win else "GAME OVER",W//2,210,TITLE,YELLOW if win else RED,True)
        text("You are the last player standing!" if win else "You were eliminated.",W//2,290,BIG,GREEN if win else WHITE,True)
        text(f"Kills: {p.kills}",W//2,370,FONT,WHITE,True)
        text("ENTER - Play Again",W//2,455,FONT,CYAN,True)
        text("ESC - Main Menu",W//2,495,FONT,WHITE,True)
        pygame.display.flip(); clock.tick(60)

def game():
    p=Player(); enemies=[Enemy(p) for _ in range(24)]
    bullets=[]; pickups=[]; buildings,trees=make_world(); zone=Zone()
    for _ in range(55):
        pickups.append(Pickup(random.randint(80,WORLD_W-80),random.randint(80,WORLD_H-80),
                              "ammo" if random.random()<.65 else "medkit"))
    paused=False
    while True:
        dt=min(clock.tick(60)/1000,.05)
        cx=clamp(p.x-W/2,0,WORLD_W-W); cy=clamp(p.y-H/2,0,WORLD_H-H)
        mx,my=pygame.mouse.get_pos(); tx,ty=mx+cx,my+cy
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN: 
                if e.key==pygame.K_p: paused=not paused
                elif e.key==pygame.K_r: p.reload()
                elif e.key==pygame.K_e: p.heal()
                elif e.key==pygame.K_ESCAPE: return "menu" 
        if not paused:
            p.update(dt); p.angle=math.atan2(ty-p.y,tx-p.x)
            if pygame.mouse.get_pressed()[0]:
                b=p.shoot(tx,ty)
                if b: bullets.append(b)
            for e in enemies:
                b=e.update(dt,p)
                if b: bullets.append(b)
            for b in bullets: b.update(dt)
            bullets=[b for b in bullets if b.life>0 and -100<b.x<WORLD_W+100 and -100<b.y<WORLD_H+100]
            for b in bullets:
                if b.owner=="player":
                    for e in enemies:
                        if dist(b.x,b.y,e.x,e.y)<e.radius+5:
                            e.health-=b.damage; b.life=0
                            if e.health<=0:
                                enemies.remove(e); p.kills+=1
                                if random.random()<.65:
                                    pickups.append(Pickup(e.x,e.y,"ammo" if random.random()<.7 else "medkit"))
                            break
                elif dist(b.x,b.y,p.x,p.y)<p.radius+5:
                    p.health-=b.damage; b.life=0
            for i in pickups[:]:
                if dist(p.x,p.y,i.x,i.y)<p.radius+i.radius:
                    if i.kind=="ammo": p.reserve_ammo+=45
                    else: p.medkits+=1
                    pickups.remove(i)
            zone.update(dt)
            if zone.outside(p.x,p.y): p.health-=8*dt
            for e in enemies:
                if zone.outside(e.x,e.y): e.health-=5*dt
            for e in enemies[:]:
                if e.health<=0: enemies.remove(e); p.kills+=1
        draw_world(cx,cy,buildings,trees)
        for i in pickups: draw_pickup(i,cx,cy)
        for e in enemies: draw_enemy(e,cx,cy)
        for b in bullets:
            sx,sy=w2s(b.x,b.y,cx,cy); pygame.draw.circle(screen,YELLOW if b.owner=="player" else ORANGE,(sx,sy),4)
        draw_player(p,cx,cy); draw_zone(zone,cx,cy); draw_hud(p,enemies,zone)
        if paused:
            pygame.draw.rect(screen,(0,0,0,160),(0,0,W,H))
            text("PAUSED",W//2,H//2-30,BIG,YELLOW,True); text("Press P to continue",W//2,H//2+40,FONT,WHITE,True)
        pygame.display.flip()
        if p.health<=0: return "restart" if game_over(False,p) else "menu"
        if not enemies: return "restart" if game_over(True,p) else "menu"

def main():
    while True:
        menu()
        while True:
            r=game()
            if r=="restart": continue
            break 

if __name__=="__main__": main()
