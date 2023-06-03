import ctypes
from ctypes.wintypes import RECT

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPixmap, QPolygon


def get_game_window():
    # Find window handle by keyword
    hwnd = ctypes.windll.user32.FindWindowW(None, None)
    window_list = []

    while hwnd != 0:
        # Get window title
        title_length = ctypes.windll.user32.GetWindowTextLengthW(hwnd) + 1
        title_buffer = ctypes.create_unicode_buffer(title_length)
        ctypes.windll.user32.GetWindowTextW(hwnd, title_buffer, title_length)

        # Check if keyword is present in the window title
        if 'War Thunder' in title_buffer.value or '戰	爭	雷	霆' in title_buffer.value:
            # Get window position and size
            rect = RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            window = {'left': rect.left, 'top': rect.top, 'right': rect.right, 'bottom': rect.bottom, 'width': rect.right - rect.left, 'height': rect.bottom - rect.top, 'title': title_buffer.value}

            window_list.append(window)

        # Find the next window
        hwnd = ctypes.windll.user32.FindWindowExW(None, hwnd, None, None)

    print('发现游戏窗口：')
    print(window_list)

    return window_list[0]


def __rotate_point__(point, origin_x, origin_y, dx, dy):

    # Calculate the new coordinates after rotation
    rotated_x = origin_x + (point.x() - origin_x) * dy - (point.y() - origin_y) * dx
    rotated_y = origin_y + (point.x() - origin_x) * dx + (point.y() - origin_y) * dy

    return QPoint(round(rotated_x), round(rotated_y))


def __get_triangle__(x, y, dx, dy, side):
    # Calculate the height and base of the triangle
    height = side * 2
    base = side

    # Calculate the coordinates of the three points of the triangle
    point1 = QPoint(round(x - (base / 2)), round(y + (height / 4)))
    point2 = QPoint(round(x + (base / 2)), round(y + (height / 4)))
    point3 = QPoint(round(x), round(y - (3 * height / 4)))

    # Rotate the points based on dx and dy
    rotated_point1 = __rotate_point__(point1, x, y, dx, dy)
    rotated_point2 = __rotate_point__(point2, x, y, dx, dy)
    rotated_point3 = __rotate_point__(point3, x, y, dx, dy)

    # Create the QPolygon with the rotated points
    triangle = QPolygon()
    triangle.append(rotated_point1)
    triangle.append(rotated_point2)
    triangle.append(rotated_point3)

    return triangle


class OverlayWindow(QtWidgets.QWidget):
    # Define a signal that takes a list of players
    players_signal = QtCore.pyqtSignal(dict)

    player_color = ()
    teammate_color = ()

    activated = False

    def __init__(self, image_buffer=None):
        super().__init__()

        self.zoom_level = 1.0
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.X11BypassWindowManagerHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        if image_buffer is not None:
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(image_buffer.getvalue())
        else:
            self.pixmap = None

        # get screen size
        screen_geometry = QtWidgets.QApplication.desktop().screenGeometry()
        self.setGeometry(screen_geometry)

        self.map_size = 300

        self.game_window = get_game_window()
        if self.game_window is None:
            raise Exception('Game window not found')
        # set the drawing area on the right side of game window
        self.draw_area = QtCore.QRect(self.game_window['left'] + self.game_window['width'] - 10 - self.map_size - 50,
                                      self.game_window['top'] + 300, self.map_size, self.map_size)
        # self.draw_area = QtCore.QRect(1000, 200, 300, 300)

        # players to be drawn
        self.players = {}

        # Connect the signal to the drawPlayers method
        self.players_signal.connect(self.__draw_players__)

        self.show()

    def paintEvent(self, event=None):
        painter = QtGui.QPainter(self)

        # Clear the widget with a completely transparent color
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 0))

        if not self.activated:
            return

        if len(self.players) > 0:
            # draw border for the draw area
            painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 100, 255), 1))
            painter.drawRect(self.draw_area)

            # draw grid for the draw area 1 to 10 and A to J
            painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 100, 255), 1))
            for i in range(1, 11):
                x = self.draw_area.x() + i * self.draw_area.width() / 10
                painter.drawLine(int(x), self.draw_area.y(), int(x), self.draw_area.y() + self.draw_area.height())
            for i in range(1, 11):
                y = self.draw_area.y() + i * self.draw_area.height() / 10
                painter.drawLine(self.draw_area.x(), int(y), self.draw_area.x() + self.draw_area.width(), int(y))

        # Draw the image
        if self.pixmap is not None:
            painter.drawPixmap(self.draw_area, self.pixmap)

        for player in self.players:

            name = player
            status = self.players[player]
            if status['type'] == 'player':
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 255), 2))
            elif status['type'] == 'teammate':
                painter.setPen(QtGui.QPen(QtGui.QColor(0, 200, 0, 255), 2))

            x = status['x'] * self.draw_area.width() + self.draw_area.x()
            y = status['y'] * self.draw_area.height() + self.draw_area.y()
            dx = status['dx']
            dy = -status['dy']

            polygon = __get_triangle__(x, y, dx, dy, 10)
            painter.drawPolygon(polygon)

            if status['type'] == 'teammate':
                # Draw player name and altitude
                text_x = int(x + 10)
                text_y = int(y)
                painter.drawText(text_x, text_y, f"{name}")
                painter.drawText(text_x + 5, text_y + 10, f"{status['altitude']}")

    def __draw_players__(self, players):
        self.players = players
        self.update()  # Trigger a repaint

    def draw_player(self, players):
        self.players_signal.emit(players)


if __name__ == '__main__':
    print(get_game_window())
