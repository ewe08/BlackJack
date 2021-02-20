import os
import sys
from itertools import product
from random import shuffle

import pygame

SUITS = ['heart', 'diamond', 'club', 'spade']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']

pygame.init()
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
FPS = 50
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
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

    def create_label(self, surface, x, y, length, height):
        surface = self.write_text(surface, length, height, x, y, font_size=self.font_size)
        self.rect = pygame.Rect(x, y, length, height)
        return surface

    def write_text(self, surface, length, height, x, y, font_size=None):
        if font_size is None:
            font_size = int(length // len(self.text))
        myFont = pygame.font.SysFont("gabriola", font_size)
        myText = myFont.render(self.text, True, self.text_color)
        surface.blit(myText, (
            (x + length / 2) - myText.get_width() / 2,
            (y + height / 2) - myText.get_height() / 2))
        return surface

    def change_text(self, text):
        self.text = text


class Button:
    def __init__(self):
        self.text_color = (0, 0, 0)
        self.font_size = None

    def create_button(self, surface, x, y, length, height, text):
        surface = self.write_text(surface, text, length, height, x, y, font_size=self.font_size)
        self.rect = pygame.Rect(x, y, length, height)
        return surface

    def write_text(self, surface, text, length, height, x, y, font_size=None):
        if font_size is None:
            font_size = int(length // len(text))
        myFont = pygame.font.SysFont("gabriola", font_size)
        myText = myFont.render(text, True, self.text_color)
        surface.blit(myText, (
            (x + length / 2) - myText.get_width() / 2,
            (y + height / 2) - myText.get_height() / 2))
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
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
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
        fon = pygame.transform.scale(load_image('background\\menu_table.png'), (width, height))
        screen.blit(fon, (0, 0))
        fon = pygame.transform.scale(load_image('background\\diamond.png'), (width // 2, height))
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
                            Game()
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

    def ask_card(self, deck):
        if self.sum_points < 21:
            card = deck.get_card()
            card.image = card.image_card
            card.change_position(self.x, self.y)
            self.p_cards.append(card)
            self.x = self.x + 30

    def draw_cards(self):
        cards_sprites.draw(screen)


class Bot:
    def __init__(self):
        self.cards = []
        self.sum_points = 0
        self.x = 400
        self.y = 100

    def change_points(self, label):
        self.sum_points = 0
        for card in self.cards:
            self.sum_points = self.sum_points + card.points
            label.change_text(str(self.sum_points))

    def ask_card(self, deck):
        if self.sum_points < 21:
            card = deck.get_card()
            card.change_position(self.x, self.y)
            self.cards.append(card)
            self.x = self.x + 30

    def draw_cards(self):
        bots_cards_sprites.draw(screen)

    def open_card(self):
        for card in self.cards:
            card.image = card.image_card


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
        self.deck = Deck(all_sprites)
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
        fon = pygame.transform.scale(load_image('background\\table.png'), (width, height))
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
                self.bot.change_points(self.labels[0])
            y += 600
        all_sprites.draw(screen)
        self.player.draw_cards()
        self.bot.draw_cards()
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
                            self.player.ask_card(self.deck)
                        elif btn[0].mouse_here(event.pos) and btn[1] == 'Open Cards':
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
            self.bot.ask_card(self.deck)
            self.player.ask_card(self.deck)
            self.player.change_points(self.labels[1])
        pygame.display.flip()

    def end_game(self):
        self.end = True
        self.bot.open_card()
        self.update_display()
        pygame.display.flip()

    def new_game(self):
        global all_sprites, cards_sprites, bots_cards_sprites
        all_sprites = pygame.sprite.Group()
        cards_sprites = pygame.sprite.Group()
        bots_cards_sprites = pygame.sprite.Group()

        if self.player.sum_points < self.bot.sum_points <= 21:
            state = "Lose"
        elif self.bot.sum_points < self.player.sum_points <= 21:
            state = "Win"
        elif self.bot.sum_points == self.player.sum_points <= 21:
            state = 'Push'
        else:
            state = 'Lose'
        NewGame(state)


class NewGame:
    def __init__(self, state):
        self.buttons = []
        self.label = Label(state)
        self.label.font_size = 78
        for text in ['Again', 'Menu']:
            new_button(text, self.buttons)
        self.main()

    def update_display(self):
        fon = pygame.transform.scale(load_image('background\\menu_table.png'), (width, height))
        screen.blit(fon, (0, 0))
        x = 525
        y = 400
        for btn in self.buttons:
            btn[0].create_button(screen, x, y, 200, 100, btn[1])
            y += 100
        self.label.create_label(screen, x, 200, 200, 100)

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
                        if btn[0].mouse_here(event.pos) and btn[1] == 'Again':
                            Game()
                        elif btn[0].mouse_here(event.pos) and btn[1] == 'Menu':
                            Menu()
            self.update_display()
            pygame.display.flip()


if __name__ == '__main__':
    menu = Menu()
