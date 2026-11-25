# 128x128 RGB565 renderer for Micro Moto.
import engine_draw

W = 128
H = 128


def rgb(r,g,b):
    return ((r&0xf8)<<8)|((g&0xfc)<<3)|(b>>3)

WHITE=rgb(255,255,255); INK=rgb(12,18,32); GOLD=rgb(255,205,70)
CYAN=rgb(60,220,240); GREEN=rgb(80,210,120); ORANGE=rgb(255,110,55)
PINK=rgb(255,75,135); RED=rgb(245,55,75); GRASS=rgb(45,145,85)
SKIES=(rgb(55,145,220),rgb(90,95,190),rgb(235,130,95))


class Renderer:
    def centered(self, s, y, c=WHITE):
        s=str(s)
        engine_draw.text(None,s,c,float((W-len(s)*5)/2),float(y),1.0,1.0,1.0)

    def text(self,s,x,y,c=WHITE):
        engine_draw.text(None,str(s),c,float(x),float(y),1.0,1.0,1.0)

    def render(self, game):
        fb=engine_draw.back_fb()
        if game.state=="title":
            fb.fill(SKIES[game.theme_idx])
            fb.fill_rect(0,88,128,40,INK)
            self.centered("MICRO MOTO",18,GOLD)
            engine_draw.circle(ORANGE,64,54,18,False,1.0)
            fb.fill_rect(49,61,30,5,INK)
            fb.fill_rect(76,53,18,5,INK)
            options=("RIDE","LEVELS","SETTINGS")
            for i,opt in enumerate(options):
                c=GOLD if i==game.title_option else WHITE
                self.centered(opt,78+i*12,c)
            return

        if game.state=="level_select":
            fb.fill(INK)
            self.centered("SELECT LEVEL",8,GOLD)
            start=(game.level_index//10)*10
            for i in range(10):
                idx=start+i
                if idx>=50: break
                row=i//5; col=i%5
                x=8+col*24; y=30+row*35
                if idx>game.unlocked_level:
                    c=rgb(70,75,90)
                elif idx==game.level_index:
                    c=GOLD
                else:
                    c=WHITE
                engine_draw.rect(c,x,y,18,20,True,1.0)
                self.text(str(idx+1),x+5,y+7,c)
            self.text("A RIDE   B BACK",12,112,WHITE)
            return

        if game.state=="settings":
            fb.fill(INK); self.centered("SETTINGS",8,GOLD)
            names=("SOUND","RUMBLE","ASSIST","THEME","SHOW TIMES")
            vals=("ON" if game.sound_on else "OFF","ON" if game.rumble_on else "OFF",("EASY","NORM","HARD")[game.assist_mode],("BLUE","PURPLE","SUNSET")[game.theme_idx],"ON" if game.show_times else "OFF")
            for i in range(5):
                c=GOLD if i==game.setting_index else WHITE
                self.text(names[i],12,30+i*15,c)
                self.text(vals[i],92,30+i*15,c)
            self.text("A/LR CHANGE",15,112,WHITE)
            return

        sky=SKIES[game.theme_idx]
        fb.fill(sky)
        fb.fill_rect(0,105,128,23,INK)

        cam=int(game.camera)
        level=game.level
        spacing=level["spacing"]
        # Terrain as heightfield segments.
        pts=[]
        for sx in range(-8,136,6):
            wx=sx+cam
            pts.append((sx, int(level["terrain"][min(len(level["terrain"])-1,max(0,int(wx/spacing)))])))
        for i in range(len(pts)-1):
            x1,y1=pts[i]; x2,y2=pts[i+1]
            engine_draw.line(GRASS,x1,y1,x2,y2,1.0)
            fb.fill_rect(x1,y1,7,128-y1,GRASS)

        # Checkpoints.
        for i,cpx in enumerate(level["checkpoints"]):
            sx=cpx-cam
            if -20<sx<148:
                ground=level["terrain"][min(len(level["terrain"])-1,max(0,int(cpx/spacing)))]
                c=GOLD if i>=game.checkpoint else GREEN
                fb.vline(int(sx),ground-30,30,c)
                engine_draw.rect(c,int(sx),ground-30,14,8,False,1.0)

        # Hazards.
        for hazard in level["hazards"]:
            sx=hazard["x"]-cam
            if sx<-30 or sx>150: continue
            wx=hazard["x"]
            ground=level["terrain"][min(len(level["terrain"])-1,max(0,int(wx/spacing)))]
            if hazard["kind"]=="spikes":
                for j in range(0,hazard["w"],5):
                    engine_draw.line(WHITE,sx+j,ground,sx+j+2,ground-8,1.0)
                    engine_draw.line(WHITE,sx+j+2,ground-8,sx+j+5,ground,1.0)
            elif hazard["kind"]=="oil":
                fb.fill_rect(int(sx),ground-3,hazard["w"],4,INK)
            else:
                fb.fill_rect(int(sx),ground-12,hazard["w"],12,ORANGE)
                fb.rect(int(sx),ground-12,hazard["w"],12,INK)

        # Finish gate.
        fx=level["finish"]-cam
        if -30<fx<150:
            ground=level["terrain"][min(len(level["terrain"])-1,max(0,int(level["finish"]/spacing)))]
            fb.vline(int(fx),ground-38,38,WHITE)
            fb.vline(int(fx+18),ground-38,38,WHITE)
            fb.fill_rect(int(fx),ground-38,18,8,GOLD)

        p=game.player
        px=int(p["x"]-cam)
        py=int(p["y"])
        if 0<px<128:
            angle=p["angle"]
            # Wheels.
            engine_draw.circle(INK,px-7,py+9,5,False,1.0)
            engine_draw.circle(INK,px+8,py+9,5,False,1.0)
            engine_draw.circle(WHITE,px-7,py+9,2,True,1.0)
            engine_draw.circle(WHITE,px+8,py+9,2,True,1.0)
            # Frame and rider, with an angle-flash during crashes.
            c=PINK if game.state=="crashed" else CYAN
            engine_draw.line(c,px-7,py+8,px,py+2,1.0)
            engine_draw.line(c,px,py+2,px+8,py+8,1.0)
            engine_draw.line(c,px-7,py+8,px+8,py+8,1.0)
            engine_draw.circle(ORANGE,px,py-7,4,False,1.0)

        minutes=int(game.elapsed)//60
        seconds=int(game.elapsed)%60
        hundredths=int((game.elapsed*100)%100)
        self.text("L%02d"%(game.level_index+1),3,3,GOLD)
        self.text("%02d:%02d.%02d"%(minutes,seconds,hundredths),70,3,WHITE)

        if game.state=="paused":
            engine_draw.rect(INK,24,42,80,44,False,0.9)
            fb.rect(24,42,80,44,WHITE)
            self.centered("PAUSED",50,WHITE)
            self.centered("A RESET",64,GOLD)
            self.centered("B/MENU RESUME",76,WHITE)
        elif game.state=="crashed":
            engine_draw.rect(INK,20,48,88,28,False,0.9)
            self.centered("CRASH!",54,RED)
            self.centered("A RESTORE",65,WHITE)
        elif game.state=="complete":
            engine_draw.rect(INK,16,42,96,44,False,0.92)
            self.centered("FINISH!",48,GOLD)
            self.centered("%02d:%02d.%02d"%(minutes,seconds,hundredths),60,WHITE)
            self.centered("A NEXT  B MENU",72,WHITE)

        if game.state=="playing":
            target=p["x"]-58
            if target>game.camera:
                game.camera+=(target-game.camera)*0.12
