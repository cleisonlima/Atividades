from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# chão
ground = Entity(model='plane', scale=(50,1,50), texture='white_cube', texture_scale=(50,50), collider='box')

# sky
Sky()

# cubo giratório
cube = Entity(model='cube', color=color.azure, scale=2, position=(3,1,3), collider='box')

# coletável (moeda)
coin = Entity(model='sphere', color=color.yellow, scale=0.4, position=(0,1,-4), collider='sphere')

# jogador
player = FirstPersonController(y=1.5, speed=6)
player.collider = BoxCollider(player, center=Vec3(0,1,0), size=Vec3(1,2,1))  # collider manual

score = 0
score_text = Text(text=f'Score: {score}', position=window.top_left, origin=(0,0), scale=2, background=True)

def respawn_coin():
    coin.position = (random.uniform(-8,8), 1, random.uniform(-8,8))
    coin.scale = 0.4
    coin.enabled = True

def update():
    global score
    cube.rotation_y += time.dt * 60

    # colisão jogador-coin
    if coin.enabled and player.collider.intersects(coin).hit:
        score += 1
        score_text.text = f'Score: {score}'
        coin.animate_scale(0.0, duration=0.2)
        coin.enabled = False
        invoke(respawn_coin, delay=2)

instructions = Text(
    'WASD mover • Espaço pular • Olhar com mouse\nPegue as moedas amarelas!',
    origin=(0,0), position=window.bottom_left + Vec2(0.02,0.02), scale=1.1
)

app.run()
