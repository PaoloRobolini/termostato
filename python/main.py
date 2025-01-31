from queue import Empty

import serial
import dearpygui.dearpygui as dpg
import multiprocessing as mp


def read_data(q):
    # crea la seriale
    porta_seriale = "COM5"
    ser = serial.Serial(porta_seriale, 9600)

    while True:
        # legge i dati (o meglio, legge i byte di dati)
        serial_data = ser.readline()

        # li converte in una stringa utf-8
        numbered_data = serial_data.decode("utf-8")

        # mette in due variabili, T e H come arduino
        t, h = numbered_data.split(' ')

        # converte in interi
        h = int(h)
        t = int(t)

        q.put([h, t])


if __name__ == '__main__':
    # creazione coda per la comunicazione dei processi
    queue = mp.Queue()

    # creazione processo per la lettura della seriale
    read_process = mp.Process(target=read_data, args=(queue,))
    read_process.start()

    # creazione gui
    dpg.create_context()
    dpg.create_viewport(title='Data Reader')

    # aggiunta delle caselle di testo contenenti le varie informazioni
    with dpg.window(label="Data Reader"):
        dpg.add_text("Data Reader")
        dpg.add_text("", tag="data")

    # inizializzazione gui
    dpg.setup_dearpygui()
    dpg.show_viewport()

    # dichiarazione lista dei dati
    data = [0, 0]

    # aggiornamento gui
    while dpg.is_dearpygui_running():
        if not queue.empty():
            try:
                data = queue.get(block=False)
            except Empty:
                continue

            dpg.set_value("data", data)

        dpg.render_dearpygui_frame()
