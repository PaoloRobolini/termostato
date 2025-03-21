from queue import Empty
from datetime import datetime
from pathlib import Path

import serial
import json
import dearpygui.dearpygui as dpg
import multiprocessing as mp

global temperature
global humidity
global time
global color_r
global color_v
global read_process
global queue


def read_data(q):
    # dichiarazione della porta seriale
    porta_seriale = "COM7"
    ser = serial.Serial(porta_seriale, 9600)
    while True:
        # legge i dati dalla porta seriale come bit
        serial_data = ser.readline()

        # converte i bit letti in caratteri utf-8
        numbered_data = serial_data.decode("utf-8")

        # mette i dati in due variabili t (temperatura) ed h (umidità)
        t, h = numbered_data.split(' ')

        # converte le due variabili in stringhe
        h = int(h)
        t = int(t)

        # mette le due variabili nella coda del processo
        q.put([h, t])


def save_data():
    # dichiarazione lista dati da salvare
    data_save = []

    # riempimento della lista con i dati
    for item in range(60):
        temp = {
            "time": time[item],
            "temperature": temperature[item],
            "humidity": humidity[item]
        }
        data_save.append(temp)

    # salvataggio su file JSON
    print("saving data")
    file_name = Path.cwd().parent / ("logs/" + datetime.now().strftime("%Y-%m-%d-%H%M") + ".json")
    with open(file_name, 'w') as outfile:
        json.dump(data_save, outfile, indent=4, ensure_ascii=False)
    print("data saved")


def exit_program():
    print("exiting program")

    dpg.stop_dearpygui()
    read_process.kill()
    queue.close()

    print("exited program")


if __name__ == '__main__':
    # creazione coda per la comunicazione dei processi
    queue = mp.Queue()

    # creazione processo per la lettura della seriale
    read_process = mp.Process(target=read_data, args=(queue,))
    read_process.start()

    # dichiarazione liste dei dati
    data = [0, 0]
    temperature = [0 for i in range(60)]
    humidity = [0 for i in range(60)]
    time = ["NONE" for i in range(60)]
    intervals = [i for i in range(1, 61)]

    # dichiarazione soglie per indicare lo stato dei led
    SOGLIA_INFERIORE = 23
    SOGLIA_SUPERIORE = 27

    # dichiarazione colori per i led
    color_r = (0, 255, 0, 255)
    color_v = (255, 0, 0, 55)

    # creazione gui
    dpg.create_context()
    dpg.create_viewport(title='Termostato', width=1450, height=950)

    # aggiunta delle caselle di testo contenenti le varie informazioni
    with dpg.window(tag="Primary Window"):
        # aggiunta dati
        dpg.add_text("", tag="temperature")
        dpg.add_text("", tag="humidity")
        dpg.add_text("", tag="leds")

        with dpg.plot(label="Temperature Variation", height=400, width=1000, tag="temperaturePlot"):
            # dichiarazione assi
            dpg.add_plot_axis(dpg.mvXAxis, label="time (s)", tag="timeAxis1")
            dpg.add_plot_axis(dpg.mvYAxis, label="temperature (C)", tag="temperatureAxis")

            # impostazione limiti degli assi
            dpg.set_axis_limits("timeAxis1", 0, 60)
            dpg.set_axis_limits("temperatureAxis", -20, 50)

            # aggiunta delle linee
            dpg.add_line_series(temperature, intervals, parent="temperatureAxis", tag="temperatureData",
                                label="Temperature")

        with dpg.plot(label="Humidity Variation", height=400, width=1000, tag="humidityPlot"):
            # dichiarazione assi
            dpg.add_plot_axis(dpg.mvXAxis, label="time (s)", tag="timeAxis2")
            dpg.add_plot_axis(dpg.mvYAxis, label="humidity (%)", tag="humidityAxis")

            # impostazione limiti degli assi
            dpg.set_axis_limits("timeAxis2", 0, 60)
            dpg.set_axis_limits("humidityAxis", 0, 100)

            # aggiunta delle linee
            dpg.add_line_series(temperature, intervals, parent="humidityAxis", tag="humidityData",
                                label="Humidity")

        # aggiunta bottone di salvataggio
        dpg.add_button(enabled=True, label="Save the last 60 seconds", tag="saveButton",
                       callback=save_data, width=400, height=100, pos=(1012, 78))
        dpg.add_button(enabled=True, label="Exit", tag="exitButton", callback=exit_program, width=400, height=100,
                       pos=(1012, 182))
        c1 = dpg.draw_circle(center=(960, 85), radius=8, color=(0, 0, 0, 255), thickness=1, fill=color_v, tag="ledR")
        c2 = dpg.draw_circle(center=(980, 85), radius=8, color=(0, 0, 0, 255), thickness=1, fill=color_r, tag="ledV")

    # inizializzazione gui
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)

    # aggiornamento gui
    while dpg.is_dearpygui_running():
        # prende i dati dalla coda se essa non è vuota
        if not queue.empty():
            try:
                data = queue.get(block=False)
            except Empty:
                continue

            # inserisce la temperatura nella lista
            temperature.append(data[1])
            temperature.pop(0)

            # inserisce l'umidità nella lista
            humidity.append(data[0])
            humidity.pop(0)

            # inserisce il tempo di orologio corrente nella lista
            time.append(datetime.now().strftime("%H:%M:%S:%ms"))
            time.pop(0)

            # if per la decisione dello stato dei led rosso e verde
            if SOGLIA_SUPERIORE > data[1] > SOGLIA_INFERIORE:
                stato_led_verde = True
                stato_led_rosso = False

                dpg.configure_item(c1, fill=(0, 255, 0, 255))
                dpg.configure_item(c2, fill=(55, 0, 0, 55))

            elif data[1] >= SOGLIA_SUPERIORE:
                stato_led_verde = False
                stato_led_rosso = True

                dpg.configure_item(c1, fill=(0, 55, 0, 55))
                dpg.configure_item(c2, fill=(255, 0, 0, 255))

            else:
                stato_led_verde = False
                stato_led_rosso = False

                dpg.configure_item(c1, fill=(0, 55, 0, 55))
                dpg.configure_item(c2, fill=(55, 0, 0, 55))

            # aggiornamento dati
            dpg.set_value("temperature", f"Temperature: {data[1]} °C")
            dpg.set_value("humidity", f"Humidity: {data[0]} %")
            dpg.set_value("leds", f"Led Verde: {stato_led_verde} | Led Rosso: {stato_led_rosso}")

            # aggiornamento grafici
            dpg.set_value("temperatureData", [intervals, temperature])
            dpg.set_value("humidityData", [intervals, humidity])

        # renderizza il frame corrente della gui
        dpg.render_dearpygui_frame()

    dpg.destroy_context()
    exit()
