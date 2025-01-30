import serial
import dearpygui.dearpygui as dpg
import multiprocessing as mp
# import imgui

def read_data(q):
    # crea la seriale
    SERIALE = "COM3"
    ser = serial.Serial(SERIALE, 9600)

    while True:
        # legge i dati (o meglio, legge i byte di dati)
        data = ser.readline()

        # li converte in una stringa utf-8
        data = data.decode("utf-8")

        # mette in due variabili, T e H come arduino
        t, h = data.split(' ')

        # converte in interi
        h = int(h)
        t = int(t)

        q.put([h, t])

    # ser.close() # chiudi la seriale


if __name__ == '__main__':
    queue = mp.Queue()
    read_process = mp.Process(target=read_data, args=(queue,))
    read_process.start()

    # creazione gui
    dpg.create_context()
    dpg.create_viewport(title='Data Reader')

    with dpg.window(label="Data Reader"):
        dpg.add_text("Data Reader")
        dpg.add_text("", tag="data")

    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        try:
            data = queue.get_nowait()
            dpg.set_value("data", data)
        except:
            continue

        dpg.render_dearpygui_frame()
