import main_window
import service

if __name__ == '__main__':
    service = service.Service(ip='127.0.0.1', port=8222, protocol='http')
    window = main_window.MainWindow(service)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
