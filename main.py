import os
import sys
from itertools import product

import pygame

buttons = []
SUITS = ['heart', 'diamond', 'club', 'spade']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']

pygame.init()
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
FPS = 50
clock = pygame.time.Clock()


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


class Menu:
    def __init__(self):
        for label in ['Start', 'Quit']:
            self.new_button(label)
        self.main()

    # Update the display and show the button
    def update_display(self):
        fon = pygame.transform.scale(load_image('background\\menu_table.png'), (width, height))
        screen.blit(fon, (0, 0))
        fon = pygame.transform.scale(load_image('background\\diamond.png'), (width // 2, height))
        screen.blit(fon, (315, 0))

        x = 525
        y = 100
        for btn in buttons:
            btn[0].create_button(screen, x, y, 200, 100, btn[1])
            y += 100

    # Run the loop
    def main(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEMOTION:
                    for btn in buttons:
                        if btn[0].mouse_here(event.pos):
                            btn[0].change_color('grey')
                        else:
                            btn[0].change_color('black')
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in buttons:
                        if btn[0].mouse_here(event.pos) and btn[1] == 'Quit':
                            terminate()
                        elif btn[0].mouse_here(event.pos) and btn[1] == 'Start':
                            Game()
                self.update_display()
                pygame.display.flip()

    def new_button(self, text):
        buttons.append((Button(), text))


class Player:
    pass


class Bot:
    pass


class Deck:
    def generate_deck(self):
        cards = []
        for suit, rank in product(SUITS, RANKS):
            if rank == 'ace':
                points = 11
            elif rank.isdigit():
                points = int(rank)
            else:
                points = 10
            img_card = load_image(suit + "/" + str(rank) + ".png")
            c = Card(points=points, rank=rank, suit=suit, sprite=img_card)
            cards.append(c)
        return cards

    def draw_deck(self, x, y):
        cover = load_image('background/cover.png')
        screen.blit(cover, x, y)


class Card:
    def __init__(self, points, rank, suit, sprite):
        self.suit = suit
        self.rank = rank
        self.points = points
        self.sprite = sprite


class Game:
    def __init__(self):
        self.buttons = []
        self.labels = []
        for text in ['Get Card', 'Open Cards']:
            self.new_button(text)
        for text in ['?', '0']:
            self.labels.append(Label(text))
        for btn in self.buttons:
            btn[0].change_color('white')
            btn[0].set_font_size(50)
        self.main()

    # Update the display and show the button
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
            y += 600

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
            self.update_display()
            pygame.display.flip()

    def new_button(self, text):
        self.buttons.append((Button(), text))


if __name__ == '__main__':
    menu = Menu()
