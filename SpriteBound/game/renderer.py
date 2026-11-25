# 128x128 RGB565 renderer for SpriteBound.
import engine_draw

W = 128
H = 128


def rgb(r,g,b):
    return ((r&0xf8)<<8)|((g&0xfc)<<3)|(b>>3)

SKY = (rgb(20,35,75), rgb(24,80,120), rgb(48,42,115))
WHITE = rgb(255,255,255)
INK = rgb(12,18,36)
GOLD = rgb(255,210,70)
GREEN = rgb(70,220,140)
PINK = rgb(255,95,135)


class Renderer:
    def text(self, s, x, y, c=WHITE):
        engine_draw.text(None, str(s), c, float(x), float(y), 1.0, 1.0, 1.0)

    def centered(self, s, y, c=WHITE):
        x = max(2, (W-len(str(s))*5)/2)
        self.text(s,x,y,c)

    def render(self, game):
        fb = engine_draw.back_fb()
        if game.state == "title":
            fb.fill(SKY[0]); fb.fill_rect(0,86,128,42,rgb(18,55,75))
            for x in range(4,128,18): fb.fill_rect(x,99+(x%3)*4,12,5,INK)
            self.centered("SPRITEBOUND",18,GOLD)
            self.centered("A VERTICAL CLIMB",31,WHITE)
            engine_draw.circle(PINK,64,63,11,False,1.0)
            fb.fill_rect(59,58,10,14,WHITE)
            fb.fill_rect(61,49,6,10,WHITE)
            self.centered("LEFT/RIGHT MOVE",82,WHITE)
            self.centered("A JUMP  -  A START",94,WHITE)
            return

        sky = SKY[game.level]
        fb.fill(sky)
        # Parallax sky bands.
        fb.fill_rect(0,94,128,34,rgb(18,55,75))
        for i in range(5):
            x = (i*31-game.elapsed*3) % 160-16
            fb.fill_rect(int(x),18+(i%3)*15,4,4,WHITE)

        sy = int(game.camera)
        for plat in game.platforms:
            y = int(plat["y"]-sy)
            if y < -8 or y > 136:
                continue
            x = int(plat["x"])
            if plat["kind"] == "goal":
                engine_draw.rect(GOLD,x,y-8,plat["w"],13,True,1.0)
                fb.fill_rect(x+plat["w"]//2-2,y-12,4,18,GOLD)
            elif plat["kind"] == "spring":
                c = PINK if plat["used"] else GOLD
                fb.fill_rect(x,y,plat["w"],5,c)
                fb.fill_rect(x+plat["w"]//2-3,y-4,6,4,c)
            elif plat["kind"] == "vanish":
                c = rgb(120,170,255) if not plat["gone"] else rgb(35,45,75)
                fb.fill_rect(x,y,plat["w"],5,c)
            else:
                fb.fill_rect(x,y,plat["w"],5,GREEN)

        p = game.player
        px = int(p["x"])
        py = int(p["y"]-sy)
        # Simple bound creature sprite.
        fb.fill_rect(px,py+4,p["w"],p["h"]-4,WHITE)
        fb.fill_rect(px+2,py,p["w"]-4,6,PINK)
        fb.pixel(px+3,py+7,INK); fb.pixel(px+6,py+7,INK)

        self.text("L"+str(game.level+1)+"/3",2,3,GOLD)
        self.text("F"+str(game.falls),96,3,WHITE)

        if game.state == "paused":
            engine_draw.rect(INK,26,42,76,44,False,0.85)
            fb.rect(26,42,76,44,WHITE)
            self.centered("PAUSED",50,WHITE)
            self.centered("A RETRY",64,WHITE)
            self.centered("B/MENU RESUME",75,WHITE)
        elif game.state == "gameover":
            self.centered("GAME OVER",52,PINK)
            self.centered("A RETRY",70,WHITE)
        elif game.state == "victory":
            fb.fill(rgb(12,20,50)); self.centered("SUMMIT!",48,GOLD)
            self.centered("YOU MADE IT",61,WHITE)
            self.centered("FALLS "+str(game.falls),75,WHITE)
