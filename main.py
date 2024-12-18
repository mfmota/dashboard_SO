from Controller.controller import DashboardController

if __name__ == "__main__":
    controller = DashboardController()
    try:
        controller.start()
    except KeyboardInterrupt:
        controller.stop()
