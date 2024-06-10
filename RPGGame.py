"""
Created on 3 Nov 2023
@author: Rosib
"""
from pygame import Rect
from GameObject import GameObject
from AssetFactory import AssetFactory
from Enum import Animation
from Enum import GameState
from File import FileManager
import pygame as pygame
import random
import pygame.freetype


class RPGGame:
    # System
    _screen: pygame.surface
    # External Assets
    _s_atlas: pygame.surface
    _c_atlas: pygame.surface
    _b_atlas: pygame.surface
    _h_atlas: pygame.surface
    _font: pygame.freetype.Font
    _font_small: pygame.freetype.Font
    _file = FileManager
    # Game logic
    _game_state = None
    _round = 0
    _character = True
    _wait_time = 0
    _change_enemy = False
    _score: int = 0
    _battle_result: bool
    _use_potion = False
    _potions = 0
    # Animated GameObjects
    _hero: [GameObject]
    _foe: [GameObject]
    _enemies: []
    _warriors: []
    _candles = GameObject
    _flag_attack: GameObject
    _flag_defend: GameObject
    _flag_wait: GameObject
    _random: GameObject
    # Sprites
    _cursor: tuple
    # Text
    _announcer_text: tuple
    _hiscore_text: tuple
    _hiscore_table: tuple
    _name = ''
    _potions_text: tuple
    # input
    _mouse_pos: pygame.Rect
    # Colliders
    _rock_collider: pygame.Rect
    _paper_collider: pygame.Rect
    _scissor_collider: pygame.Rect
    _potion_collider: pygame.Rect
    # Animation logic
    _arrived = False
    _move_hero = False
    _move_foe = False

    def __init__(self):
        self._screen = pygame.display.set_mode((960, 540), 0, 0, 0, 1)
        pygame.display.set_caption("Ultrasword - The RPG Game")
        self._file = FileManager("Data/Scores.txt")
        self._game_state = GameState.START
        pygame.mouse.set_visible(False)

    @property
    def game_state(self):
        return self._game_state

    @game_state.setter
    def game_state(self, new_state):
        self._game_state = new_state

    def load_content(self):
        # Load contents
        self._s_atlas = pygame.image.load('Assets/screen_atlas.png').convert_alpha()
        self._c_atlas = pygame.image.load('Assets/character_atlas.png').convert_alpha()
        self._b_atlas = pygame.image.load('Assets/background_atlas.png').convert_alpha()
        self._h_atlas = pygame.image.load('Assets/hud_atlas.png').convert_alpha()
        self._font = pygame.freetype.Font('Assets/fonts/Alkhemikal.ttf', 35)
        self._font_small = pygame.freetype.Font('Assets/fonts/Alkhemikal.ttf', 25)

    def initialize(self):
        pygame.init()
        # Load all external Assets
        self.load_content()
        # Initialize game state
        self._game_state = GameState.START
        # cursor
        self._cursor = self._h_atlas, (0, 0), pygame.Rect(558, 0, 28, 28)
        # Asset creation
        factory = AssetFactory(self._c_atlas, self._b_atlas, self._h_atlas)
        # Characters
        samurai = GameObject(pygame.Vector2(200, 120), factory.get_asset(2), 500, 5000, 75)
        knight = GameObject(pygame.Vector2(200, 120), factory.get_asset(1), 500, 2500, 100)
        # Enemies
        skeleton = GameObject(pygame.Vector2(500, 120), factory.get_asset(3), 500, 6000, 75)
        skeleton2 = GameObject(pygame.Vector2(500, 120), factory.get_asset(4), 600, 4000, 80)
        crow = GameObject(pygame.Vector2(500, 120), factory.get_asset(5), 700, 2000, 100)
        self._enemies = [skeleton, skeleton2, crow]
        self._warriors = [samurai, knight]
        self._hero = samurai
        self._foe = skeleton
        # BG
        self._candles = GameObject(pygame.Vector2(0, 134), factory.get_asset(20), 0, 0, 0)
        # HUD
        self._flag_attack = GameObject(pygame.Vector2(50, 100), factory.get_asset(21), 0, 0, 0)
        self._flag_defend = GameObject(pygame.Vector2(50, 100), factory.get_asset(22), 0, 0, 0)
        self._flag_wait = GameObject(pygame.Vector2(50, 100), factory.get_asset(23), 0, 0, 0)
        self._random = GameObject(pygame.Vector2(786, 252), factory.get_asset(24), 0, 0, 0)
        # colliders
        self._rock_collider = pygame.Rect(71, 254, 50, 50)
        self._paper_collider = pygame.Rect(117, 254, 50, 50)
        self._scissor_collider = pygame.Rect(163, 254, 50, 50)
        self._potion_collider = pygame.Rect(35, 350, 24, 24)
        # Texts
        self._announcer_text = self._font.render("Wait until is time to take action!", (255, 255, 255))
        self._hiscore_text = self._font.render("", (255, 255, 255))
        self._hiscore_table = self._font.render("", (255, 255, 255))
        self._potions_text = self._font_small.render("", (255, 255, 255))
        self._character = True

    def update(self, delta_time):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            global playing
            playing = False

        if keys[pygame.K_g]:
            self._score = 100
            self._game_state = GameState.GAMEOVER

        match self._game_state:
            case GameState.START:
                if not self._wait_time > 0:
                    if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]:
                        self._game_state = GameState.CHARACTER_SELECT
                        self._wait_time = 10
                    if pygame.MOUSEBUTTONUP:
                        clic = pygame.mouse.get_pressed(num_buttons=3)
                        if clic[0]:
                            self._game_state = GameState.CHARACTER_SELECT
                            self._wait_time = 10
                        if clic[2]:
                            self._game_state = GameState.HISCORE
                            self._wait_time = 10

            case GameState.HISCORE:
                if not self._wait_time > 0:
                    if pygame.MOUSEBUTTONUP:
                        clic = pygame.mouse.get_pressed(num_buttons=3)
                        if clic[2]:
                            self._game_state = GameState.START
                            self._wait_time = 10

            case GameState.CHARACTER_SELECT:
                if not self._wait_time > 0:
                    if pygame.MOUSEBUTTONUP:
                        clic = pygame.mouse.get_pressed(num_buttons=3)
                        pos = pygame.mouse.get_pos()
                        if clic[2]:
                            self._game_state = GameState.START
                            self._wait_time = 10
                        if pos[0] > 30 and pos[0] < 455 and pos[1] > 135 and pos[1] < 430:
                            self._character = True
                            self._hero = self._warriors[0]
                            self._potions = 2
                            if clic[0]:
                                self._game_state = GameState.BATTLE
                                self._wait_time = 20
                        elif pos[0] > 495 and pos[0] < 920 and pos[1] > 135 and pos[1] < 430:
                            self._character = False
                            self._hero = self._warriors[1]
                            self._potions = 1
                            if clic[0]:
                                self._game_state = GameState.BATTLE
                                self._wait_time = 10

            case GameState.BATTLE:
                if self._wait_time <= 0:
                    if self._hero.stamina >= self._hero.max_stamina or self._foe.stamina >= self._foe.max_stamina:
                        self._foe.choice = cpu_random_choice()
                        if self._hero.stamina >= self._hero.max_stamina:
                            self._announcer_text = self._font.render("Time to attack!, choose wisely!", (255, 255, 255))
                        else:
                            self._announcer_text = self._font.render("Time to defend yourself!, choose wisely!",
                                                                     (255, 255, 255))
                        self._hero.choice = self.mouse_events(0)
                        if not self._hero.choice == 0:
                            if self._hero.stamina >= self._hero.max_stamina:
                                attacker, defender = self._hero, self._foe
                                self._move_hero = True
                            else:
                                attacker, defender = self._foe, self._hero
                                self._move_foe = True
                            self._battle_result = battle(attacker.choice, defender.choice)

                            if self._battle_result:
                                defender.health = defender.health - attacker.strength
                                attacker.play_animation(Animation.ATTACK)
                                if defender.health <= 0:
                                    defender.play_animation(Animation.DEAD)
                                else:
                                    defender.play_animation(Animation.DAMAGE)
                            else:
                                defender.play_animation(Animation.DEFEND)
                                attacker.play_animation(Animation.ATTACK)

                            if self._hero.stamina >= self._hero.max_stamina:
                                if self._battle_result:
                                    self._announcer_text = self._font.render(
                                        f"The attack has reduced the enemy's health by  {self._hero.strength}",
                                        (255, 255, 255))
                                    self._score = self._score + 10
                                    self._wait_time = 150
                                else:
                                    self._announcer_text = self._font.render(
                                        "The attack has been blocked by the enemy!", (255, 255, 255))
                                    self._wait_time = 150
                                self._foe.health = defender.health
                                self._hero.stamina = 0
                            else:
                                if self._battle_result:
                                    self._announcer_text = self._font.render(
                                        f"The attack has reduced the Hero's health by {self._foe.strength} points",
                                        (255, 255, 255))
                                    self._score = self._score - 5
                                    self._wait_time = 150
                                else:
                                    self._announcer_text = self._font.render(
                                        "The attack has been blocked by the Hero!", (255, 255, 255))
                                    self._wait_time = 150
                                self._hero.health = defender.health
                                self._foe.stamina = 0

                            if self._hero.health <= 0:
                                self._wait_time = 180
                                self._announcer_text = self._font.render(f"You are dead!", (255, 255, 255))
                            if self._foe.health <= 0:
                                self._wait_time = 180
                                self._announcer_text = self._font.render(f"The enemy is dead!", (255, 255, 255))
                    else:
                        self._hero.stamina += delta_time
                        self._foe.stamina += delta_time

                if self._wait_time <= 0:
                    if self._foe.health <= 0:
                        if self._round >= 2:
                            self._game_state = GameState.GAMEOVER
                        else:
                            self._potions += 1
                            self._round += 1
                            self._foe = self._enemies[self._round]
                            self._announcer_text = self._font.render("A new foe has appeared! do your best hero!",
                                                                     (255, 255, 255))
                    if self._hero.health <= 0:
                        self._game_state = GameState.GAMEOVER

                if self._move_hero:
                    self.move_hero(delta_time)
                if self._move_foe:
                    self.move_foe(delta_time)

                # BG elements
                self._candles.__update__(delta_time)
                # Character elements
                self._hero.__update__(delta_time)
                self._foe.__update__(delta_time)
                # HUD elements
                self._flag_attack.__update__(delta_time)
                self._flag_defend.__update__(delta_time)
                self._flag_wait.__update__(delta_time)
                self._random.__update__(delta_time)

            case self._game_state.GAMEOVER:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER] and len(self._name) > 0:
                    self._file.add_new_score(f"{self._name}" + " " + f"{self._score}")
                    self._game_state = GameState.HISCORE
                    self._name = ''
                    self._hero.health = self._hero.max_health
                    self._hero.current_animation = Animation.IDLE
                    self._hero.stamina = 0
                    for enemy in self._enemies:
                        enemy.health = enemy.max_health
                        enemy.current_animation = Animation.IDLE
                        enemy.stamina = 0
                    self._round = 0
                    self._foe = self._enemies[self._round]

        if self._wait_time > 0:
            self._wait_time -= 1
        # Update mouse position for collision calculations
        self._mouse_pos = pygame.Rect(*pygame.mouse.get_pos(), 1, 1)

    def draw(self):
        match self._game_state:
            case GameState.START:
                self._screen.blit(self._s_atlas, (0, 0), pygame.Rect(0, 1084, 960, 540))  # Background

            case GameState.CHARACTER_SELECT:
                if self._character:
                    self._screen.blit(self._s_atlas, (0, 0), pygame.Rect(0, 0, 960, 540))  # Background
                else:
                    self._screen.blit(self._s_atlas, (0, 0), pygame.Rect(962, 0, 960, 540))  # Background

            case GameState.HISCORE:
                scores_table_read = self._file.read_file_hiscore()
                self._screen.blit(self._s_atlas, (0, 0), pygame.Rect(0, 542, 960, 540))  # Background
                print_x = 380
                print_y = 160
                counter = 0
                while counter < len(scores_table_read):
                    self._hiscore_table = self._font.render(f'{scores_table_read[counter][0]}', (0, 255, 0))
                    self._screen.blit(self._hiscore_table[0], (print_x, print_y))
                    self._hiscore_table = self._font.render(f'{scores_table_read[counter][1]}', (0, 255, 0))
                    self._screen.blit(self._hiscore_table[0], (print_x + 150, print_y))
                    counter = counter + 1
                    print_y = print_y + 50

            case GameState.BATTLE:
                # BG elements
                self._screen.blit(self._b_atlas, (0, 0), pygame.Rect(1000, 0, 960, 540))  # Background
                self._candles.__draw__(self._screen)  # Candles animation per frame
                # HUD elements
                self.draw_hud()
                self._screen.blit(self._h_atlas, (0, 435), pygame.Rect(0, 526, 958, 102))  # Announcer
                self._screen.blit(self._announcer_text[0], (45, 460))
                self._hiscore_text = self._font.render(f"Score: {self._score}", (255, 255, 255))
                self._screen.blit(self._hiscore_text[0], (765, 20))

                if self._arrived:
                    if self._battle_result:
                        pygame.draw.rect(self._screen, (100, 0, 10), pygame.Rect(0, 0, 960, 540))
                    else:
                        pygame.draw.rect(self._screen, (92, 93, 113), pygame.Rect(0, 0, 960, 540))
                if self._use_potion:
                    pygame.draw.rect(self._screen, (85, 255, 0), pygame.Rect(0, 0, 960, 540))
                    self._use_potion = False

                # Characters elements
                self._hero.__draw__(self._screen)
                self._foe.__draw__(self._screen)

            case GameState.GAMEOVER:
                self._name = self._name.upper()
                self._screen.blit(self._s_atlas, (0, 0), pygame.Rect(962, 542, 960, 540))  # Background
                self._hiscore_text = self._font.render(f'Score : {self._score}', (0, 255, 0))
                self._screen.blit(self._hiscore_text[0], (380, 250))
                self._hiscore_text = self._font.render(f'{self._name}', (0, 255, 0))
                self._screen.blit(self._hiscore_text[0], (550, 430))

        # Cursor
        self.mouse_events(1)  # Draw any mouse-over interaction
        self._screen.blit(self._cursor[0], pygame.mouse.get_pos(), self._cursor[2])

    def draw_bar(self, pos, size, border_c, bar_c, progress, bar_type):
        inner_pos = (pos.x + 2, pos.y + 2)
        inner_size = ((size[0] - 4) * progress, size[1] - 4)
        pygame.draw.rect(self._screen, border_c, (*pos, *size), 2)
        pygame.draw.rect(self._screen, bar_c, (*inner_pos, *inner_size))
        if bar_type:
            self._screen.blit(self._h_atlas, (pos.x - 25, pos.y - 5), pygame.Rect(438, 0, 24, 24))
        else:
            self._screen.blit(self._h_atlas, (pos.x - 25, pos.y - 5), pygame.Rect(462, 0, 24, 24))

    def draw_hud(self):
        flag_pole_sprite_rect: Rect = pygame.Rect(846, 54, 14, 170)
        scroll_hero_active_rect: Rect = pygame.Rect(0, 458, 208, 68)
        scroll_hero_disabled_rect: Rect = pygame.Rect(0, 390, 208, 68)
        scroll_hero_empty_rect: Rect = pygame.Rect(0, 254, 208, 68)
        scroll_foe_rect: Rect = pygame.Rect(2, 324, 72, 64)

        self._screen.blit(self._h_atlas, (38, 100), flag_pole_sprite_rect)  # Flag pole sprite
        flag_sprite = self._flag_defend
        scroll_rect = scroll_hero_active_rect

        if self._hero.stamina >= self._hero.max_stamina:
            flag_sprite = self._flag_attack
            scroll_rect = scroll_hero_active_rect
        if self._hero.stamina < self._hero.max_stamina and self._foe.stamina < self._foe.max_stamina:
            flag_sprite = self._flag_wait
            scroll_rect = scroll_hero_disabled_rect

        flag_sprite.__draw__(self._screen)
        self._screen.blit(self._h_atlas, (37, 244), scroll_rect)  # Hero's Scroll sprite - Attack mode
        self._screen.blit(self._h_atlas, (775, 244), scroll_foe_rect)  # Foe's Scroll sprite

        if self._wait_time > 0:
            match self._foe.choice:
                case 1:
                    self._screen.blit(self._h_atlas, (786, 252), pygame.Rect(150, 0, 50, 50))
                case 2:
                    self._screen.blit(self._h_atlas, (786, 252), pygame.Rect(200, 0, 50, 50))
                case 3:
                    self._screen.blit(self._h_atlas, (786, 252), pygame.Rect(250, 0, 50, 50))

            match self._hero.choice:
                case 1:
                    self._screen.blit(self._h_atlas, (71, 254), pygame.Rect(150, 0, 50, 50))
                case 2:
                    self._screen.blit(self._h_atlas, (117, 254), pygame.Rect(200, 0, 50, 50))
                case 3:
                    self._screen.blit(self._h_atlas, (163, 254), pygame.Rect(250, 0, 50, 50))

        if self._hero.stamina >= self._hero.max_stamina or self._foe.stamina >= self._foe.max_stamina:
            self._screen.blit(self._h_atlas, (775, 244), scroll_foe_rect)
            self._random.__draw__(self._screen)

        # Hero bars
        self.draw_bar(pygame.Vector2(60, 315), (180, 12), (0, 0, 0), (40, 80, 150),
                      self._hero.stamina / self._hero.max_stamina, False)  # Health Bar
        self.draw_bar(pygame.Vector2(60, 333), (180, 12), (0, 0, 0), (100, 0, 10),
                      self._hero.health / self._hero.max_health, True)  # Stamina Bar
        # Foe bars
        self.draw_bar(pygame.Vector2(725, 315), (180, 12), (0, 0, 0), (40, 80, 150),
                      self._foe.stamina / self._foe.max_stamina, False)  # Health Bar
        self.draw_bar(pygame.Vector2(725, 333), (180, 12), (0, 0, 0), (100, 0, 10),
                      self._foe.health / self._foe.max_health, True)  # Stamina Bar

        # potions
        self._screen.blit(self._h_atlas, (35, 350), pygame.Rect(486, 0, 24, 24))
        self._potions_text = self._font_small.render(f" x {self._potions}", (255, 255, 255))
        self._screen.blit(self._potions_text[0], (55, 353))

    def move_hero(self, delta_time):
        if self._hero.position[0] < 400 and not self._arrived:
            self._hero.position = (self._hero.position[0] + delta_time, self._hero.position[1])
        else:
            self._arrived = True
            if self._hero.position[0] > 200 and self._arrived:
                self._hero.position = (self._hero.position[0] - delta_time, self._hero.position[1])
            else:
                self._move_hero = False
                self._arrived = False

    def move_foe(self, delta_time):
        if self._foe.position[0] > 300 and not self._arrived:
            self._foe.position = (self._foe.position[0] - delta_time, self._foe.position[1])
        else:
            self._arrived = True
            if self._foe.position[0] < 500 and self._arrived:
                self._foe.position = (self._foe.position[0] + delta_time, self._foe.position[1])
            else:
                self._move_foe = False
                self._arrived = False

    def mouse_events(self, mouse_event_type):
        collide_rock = pygame.Rect.colliderect(self._rock_collider, self._mouse_pos)
        collide_paper = pygame.Rect.colliderect(self._paper_collider, self._mouse_pos)
        collide_scissor = pygame.Rect.colliderect(self._scissor_collider, self._mouse_pos)
        collide_potion = pygame.Rect.colliderect(self._potion_collider, self._mouse_pos)

        if mouse_event_type == 0:
            clic = pygame.mouse.get_pressed(num_buttons=3)
            if clic[0]:
                if collide_rock:
                    return 1
                elif collide_paper:
                    return 2
                elif collide_scissor:
                    return 3
                elif collide_potion:
                    if self._potions > 0:
                        self._potions -= 1
                        self._use_potion = True
                        self._wait_time = 60
                        self._announcer_text = self._font.render(
                            "You have used a potion, your health has been restored 100 points",
                            (255, 255, 255))
                        if (self._hero.health + 100) <= self._hero.max_health:
                            self._hero.health += 100
                        else:
                            self._hero.health = self._hero.max_health
            else:
                return 0

        if mouse_event_type == 1:
            if self._hero.stamina >= self._hero.max_stamina or self._foe.stamina >= self._foe.max_stamina:
                if collide_rock:
                    self._screen.blit(self._h_atlas, (71, 254), pygame.Rect(150, 0, 50, 50))
                elif collide_paper:
                    self._screen.blit(self._h_atlas, (117, 254), pygame.Rect(200, 0, 50, 50))
                elif collide_scissor:
                    self._screen.blit(self._h_atlas, (163, 254), pygame.Rect(250, 0, 50, 50))
                elif collide_potion:
                    self._screen.blit(self._h_atlas, (35, 350), pygame.Rect(486, 24, 24, 24))
        return 0

    # Function to handle text input
    def handle_input(self, event):
        if event.type == pygame.TEXTINPUT:
            for char in event.text:
                if char.isalpha():  # Accept only letters
                    if len(self._name) < 5:
                        self._name += char
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self._name = self._name[:-1]


def cpu_random_choice():
    # Generate a random choice for the computer
    choices = [1, 2, 3]
    computer_choice = random.choice(choices)
    return computer_choice


def battle(attacker, defender):
    if attacker == defender:
        return True
    elif (attacker == 1 and defender == 3) or (attacker == 2 and defender == 1) or (
            attacker == 3 and defender == 2):
        return True
    else:
        return False


game = RPGGame()
game.initialize()
clock = pygame.time.Clock()
playing = True

# Game loop
while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
        if game.game_state == GameState.GAMEOVER:
            game.handle_input(event)

    game.update(clock.tick(60))
    game.draw()
    pygame.display.update()

pygame.quit()
