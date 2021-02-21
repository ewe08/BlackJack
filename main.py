import os
import sys
from itertools import product
from random import shuffle

import pygame

SUITS = ['heart', 'diamond', 'club', 'spade']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']

pygame.init()
pygame.mixer.music.load('sounds\\music.mp3')
pygame.mixer.music.set_volume(0.15)
pygame.mixer.music.play(-1)
size = WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
lobby_sprites = pygame.sprite.Group()
cards_sprites = pygame.sprite.Group()
bots_cards_sprites = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Label:
    def __init__(self, text):
        self.text = text
        self.text_color = (255, 255, 225)
        self.font_size = 40
        self.rect = None

    def create_label(self, surface, x, y, length, height):
        surface = self.write_text(surface, length, height, x, y, font_size=self.font_size)
        self.rect = pygame.Rect(x, y, length, height)
        return surface

    def write_text(self, surface, length, height, x, y, font_size=None):
        if font_size is None:
            font_size = int(length // len(self.text))
        my_font = pygame.font.SysFont("gabriola", font_size)
        my_text = my_font.render(self.text, True, self.text_color)
        surface.blit(my_text, (
            (x + length / 2) - my_text.get_width() / 2,
            (y + height / 2) - my_text.get_height() / 2))
        return surface

    def change_text(self, text):
        self.text = text


class Button:
    def __init__(self):
        self.was_sound = False
        self.sound = pygame.mixer.Sound('sounds/button.wav')
        self.text_color = (0, 0, 0)
        self.font_size = None
        self.rect = None

    def create_button(self, surface, x, y, length, height, text):
        surface = self.write_text(surface, text, length, height, x, y, font_size=self.font_size)
        self.rect = pygame.Rect(x, y, length, height)
        return surface

    def write_text(self, surface, text, length, height, x, y, font_size=None):
        if font_size is None:
            font_size = int(length // len(text))
        my_font = pygame.font.SysFont("gabriola", font_size)
        my_text = my_font.render(text, True, self.text_color)
        surface.blit(my_text, (
            (x + length / 2) - my_text.get_width() / 2,
            (y + height / 2) - my_text.get_height() / 2))
        return surface

    def change_color(self, color):
        self.text_color = color

    def set_font_size(self, px):
        self.font_size = px

    def mouse_here(self, mouse):
        try:
            if mouse[0] > self.rect.topleft[0]:
                if mouse[1] > self.rect.topleft[1]:
                    if mouse[0] < self.rect.bottomright[0]:
                        if mouse[1] < self.rect.bottomright[1]:
                            if not self.was_sound:
                                self.sound.play()
                                self.was_sound = True
                            return True
                        else:
                            self.was_sound = False
                            return False
                    else:
                        self.was_sound = False
                        return False
                else:
                    self.was_sound = False
                    return False
            else:
                self.was_sound = False
                return False
        except AttributeError:
            pass


def new_button(text, array):
    array.append((Button(), text))


class Menu:
    def __init__(self):
        self.buttons = []
        for label in ['Start', 'Quit']:
            new_button(label, self.buttons)
        self.main()

    # Update the display and show the button
    def update_display(self):
        fon = pygame.transform.scale(load_image('background\\menu_table.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        fon = pygame.transform.scale(load_image('background\\diamond.png'), (WIDTH // 2, HEIGHT))
        screen.blit(fon, (315, 0))

        x = 525
        y = 100
        for btn in self.buttons:
            btn[0].create_button(screen, x, y, 200, 100, btn[1])
            y += 100

    def main(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEMOTION:
                    for btn in self.buttons:
                        if btn[0].mouse_here(event.pos):
                            btn[0].change_color('grey')
                        else:
                            btn[0].change_color('black')
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in self.buttons:
                        if btn[0].mouse_here(event.pos) and btn[1] == 'Quit':
                            terminate()
                        elif btn[0].mouse_here(event.pos) and btn[1] == 'Start':
                            lobby()
                self.update_display()
                pygame.display.flip()


class Player:
    def __init__(self):
        self.p_cards = []
        self.sum_points = 0
        self.x = 400
        self.y = 600

    def change_points(self, label):
        self.sum_points = 0
        for card in self.p_cards:
            self.sum_points = self.sum_points + card.points
            label.change_text(str(self.sum_points))

    def ask_card(self, deck, game):
        if self.sum_points < 21:
            game.card_sound.play()
            card = deck.get_card()
            card.image = card.image_card
            card.change_position(self.x, self.y)
            self.p_cards.append(card)
            self.x = self.x + 60


class Bot:
    def __init__(self):
        self.cards = []
        self.sum_points = 0
        self.x = 400
        self.y = 100

    def change_points(self):
        self.sum_points = 0
        for card in self.cards:
            self.sum_points = self.sum_points + card.points

    def return_points(self, label):
        label.change_text(str(self.sum_points))

    def ask_card(self, deck):
        if self.sum_points < 21:
            card = deck.get_card()
            card.change_position(self.x, self.y)
            self.cards.append(card)
            self.change_points()
            self.x = self.x + 60

    def open_card(self):
        for card in self.cards:
            card.image = card.image_card

    def give_card(self):
        if self.sum_points < 16:
            self.ask_card(deck_of_cards)
            return True
        return False


def deck_generation():
    cards = []
    for suit, rank in product(SUITS, RANKS):
        if rank == 'ace':
            points = 11
        elif rank.isdigit():
            points = int(rank)
        else:
            points = 10
        img_card = load_image(suit + "/" + str(rank) + ".png")
        c = Card(cards_sprites)
        c.set_card(points=points, rank=rank, suit=suit)
        c.set_image(img_card)
        cards.append(c)
    return cards


class Deck(pygame.sprite.Sprite):
    cover = load_image('background/cover.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Deck.cover
        self.rect = self.image.get_rect()
        self.rect.x = 500
        self.rect.y = 300
        self.cards = deck_generation()
        shuffle(self.cards)

    def get_card(self):
        return self.cards.pop()


class Card(pygame.sprite.Sprite):
    cover = load_image('background/cover.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Card.cover
        self.rect = self.image.get_rect()
        self.rect.x = -100
        self.rect.y = 0
        self.image_card = None
        self.suit = None
        self.rank = None
        self.points = None
        self.sprite = None

    def set_card(self, points, rank, suit):
        self.suit = suit
        self.rank = rank
        self.points = points

    def set_image(self, image):
        self.image_card = image

    def change_position(self, x, y):
        self.rect.x = x
        self.rect.y = y


class Game:
    def __init__(self):
        global deck_of_cards
        deck_of_cards = Deck(all_sprites)
        self.card_sound = pygame.mixer.Sound('sounds/card.wav')
        self.player = Player()
        self.bot = Bot()
        self.buttons = []
        self.labels = []
        for text in ['Get Card', 'Open Cards']:
            new_button(text, self.buttons)
        for text in ['?', '0']:
            self.labels.append(Label(text))
        for btn in self.buttons:
            btn[0].change_color('white')
            btn[0].set_font_size(50)
        self.start = True
        self.end = False
        self.main()

    def update_display(self):
        fon = pygame.transform.scale(load_image('background\\table.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        x = 1050
        y = 25
        for btn in self.buttons:
            btn[0].create_button(screen, x, y, 200, 100, btn[1])
            y += 600
        x = 125
        y = 25
        for label in self.labels:
            label.create_label(screen, x, y, 200, 100)
            self.player.change_points(self.labels[1])
            if self.end:
                self.bot.return_points(self.labels[0])
            y += 600
        all_sprites.draw(screen)
        cards_sprites.draw(screen)
        bots_cards_sprites.draw(screen)
        pygame.display.flip()

    def main(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEMOTION:
                    for btn in self.buttons:
                        if btn[0].mouse_here(event.pos):
                            btn[0].change_color('red')
                        else:
                            btn[0].change_color('white')
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in self.buttons:
                        if btn[0].mouse_here(event.pos) and btn[1] == 'Get Card':
                            self.player.ask_card(deck_of_cards, self)
                            self.bot.give_card()
                        elif btn[0].mouse_here(event.pos) and btn[1] == 'Open Cards':
                            while self.bot.give_card():
                                pass
                            self.end_game()
            self.update_display()
            if self.start:
                self.start_the_game()
                self.start = False
            if self.end:
                pygame.time.delay(1000)
                self.new_game()
            pygame.display.flip()

    def start_the_game(self):
        for _ in range(2):
            self.bot.ask_card(deck_of_cards)
            self.player.ask_card(deck_of_cards, self)
            self.player.change_points(self.labels[1])
        pygame.display.flip()

    def end_game(self):
        self.end = True
        self.bot.open_card()
        self.update_display()
        pygame.display.flip()

    def new_game(self):
        global all_sprites, cards_sprites, bots_cards_sprites, deck_of_cards
        all_sprites = pygame.sprite.Group()
        cards_sprites = pygame.sprite.Group()
        bots_cards_sprites = pygame.sprite.Group()
        deck_of_cards = Deck(all_sprites)

        if 21 >= self.bot.sum_points > self.player.sum_points or \
                self.bot.sum_points <= 21 < self.player.sum_points:
            state = "Lose"
        elif 21 >= self.player.sum_points > self.bot.sum_points or \
                self.player.sum_points <= 21 < self.bot.sum_points:
            state = "Win"
        elif self.bot.sum_points == self.player.sum_points <= 21:
            state = 'Push'
        else:
            state = 'Lose'
        NewGame(state)


class Win(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class NewGame:
    def __init__(self, state):
        self.buttons = []
        self.state = state
        self.label = Label(state)
        self.label.font_size = 78
        self.crown = Win(load_image("spritesheets/win.png"), 8, 1, 575, 150)
        self.crown_sprite = pygame.sprite.GroupSingle(self.crown)
        for text in ['Play', 'Lobby']:
            new_button(text, self.buttons)
        self.main()

    def update_display(self):
        fon = pygame.transform.scale(load_image('background\\menu_table.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        x = 525
        y = 400
        for btn in self.buttons:
            btn[0].create_button(screen, x, y, 200, 100, btn[1])
            y += 100
        self.label.create_label(screen, x, 200, 200, 100)
        if self.state == 'Win':
            clock.tick(10)
            self.crown.update()
            self.crown_sprite.draw(screen)

    def main(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEMOTION:
                    for btn in self.buttons:
                        if btn[0].mouse_here(event.pos):
                            btn[0].change_color('red')
                        else:
                            btn[0].change_color('white')
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in self.buttons:
                        if btn[0].mouse_here(event.pos) and btn[1] == 'Play':
                            all_sprites.remove(self.crown)
                            Game()
                        elif btn[0].mouse_here(event.pos) and btn[1] == 'Lobby':
                            all_sprites.remove(self.crown)
                            lobby()
            self.update_display()
            pygame.display.flip()


class LobbyPlayer(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(lobby_sprites)
        self.sound = pygame.mixer.Sound('sounds/step.wav')
        self.left = True
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        global hero_pos

        if pygame.sprite.collide_mask(self, table):
            hero_pos = (self.rect.x - 10, self.rect.y)
            lobby_sprites.remove(self)
            NewGame('Start?')
        self.sound.play()
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)


class Table(pygame.sprite.Sprite):
    image = load_image('background/table_lobby.png')

    def __init__(self):
        super().__init__(lobby_sprites)
        self.image = Table.image
        self.rect = self.image.get_rect()
        self.rect.x = 1000
        self.rect.y = 500
        self.mask = pygame.mask.from_surface(self.image)


class Platform(pygame.sprite.Sprite):
    image = load_image('background/pol.png')

    def __init__(self):
        super().__init__(lobby_sprites)
        self.image = Platform.image
        self.rect = self.image.get_rect()


hero_pos = (100, 510)


def lobby():
    global table
    x, y = hero_pos
    for i in range(15):
        p = Platform()
        p.rect.bottom = HEIGHT
        p.rect.x = i * 100
    table = Table()
    hero = LobbyPlayer(load_image("hero/player.png", colorkey=-1), 8, 1, x, y)
    while True:
        fon = pygame.transform.scale(load_image('background\\lobby.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            hero.rect.x += 12
            hero.update()
            hero.flip()
        if keys[pygame.K_LEFT]:
            hero.rect.x -= 12
            hero.update()
        clock.tick(20)
        lobby_sprites.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    FPS = 50
    clock = pygame.time.Clock()
    deck_of_cards = None
    menu = Menu()
