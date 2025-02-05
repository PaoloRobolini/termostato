from queue import Empty
from datetime import datetime

import serial
import json
import dearpygui.dearpygui as dpg
import multiprocessing as mp

global temperature
global humidity
global time


def read_data(q):
    # crea la seriale
    porta_seriale = "COM10"
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

        # mette le due variabili nella coda del processo
        q.put([h, t])


def save_data():
    data_save = []

    for item in range(60):
        temp = {
            "time": time[item],
            "temperature": temperature[item],
            "humidity": humidity[item]
        }
        data_save.append(temp)

    file_name = datetime.now().strftime("%Y%m%d%H%M") + ".json"
    with open(file_name, "w") as outfile:
        json.dump(data_save, outfile,indent=4, ensure_ascii=False)


SOGLIA_INFERIORE = 25
SOGLIA_SUPERIORE = 27

if __name__ == '__main__':
    # creazione coda per la comunicazione dei processi
    queue = mp.Queue()

    # creazione processo per la lettura della seriale
    read_process = mp.Process(target=read_data, args=(queue,))
    read_process.start()

    # dichiarazione lista dei dati
    data = [0, 0]
    temperature = [0 for i in range(60)]
    humidity = [0 for i in range(60)]
    time = ["NONE" for i in range(60)]
    intervals = [i for i in range(1, 61)]

    # creazione gui
    dpg.create_context()
    dpg.create_viewport(title='Termostato', width=1600, height=900)

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

        dpg.add_button(enabled=True, label="Save the last 60 seconds", tag="saveButton",
                       callback=save_data, width=400, height=100)

    # inizializzazione gui
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)

    # aggiornamento gui
    while dpg.is_dearpygui_running():
        if not queue.empty():
            try:
                data = queue.get(block=False)
            except Empty:
                continue

            temperature.append(data[1])
            temperature.pop(0)

            humidity.append(data[0])
            humidity.pop(0)

            time.append(datetime.now().strftime("%H:%M:%S"))
            time.pop(0)

            stato_led_verde = False
            stato_led_rosso = False

            if SOGLIA_SUPERIORE >= data[1] > SOGLIA_INFERIORE:
                stato_led_verde = True
                stato_led_rosso = False

            elif data[1] > SOGLIA_SUPERIORE:
                stato_led_verde = False
                stato_led_rosso = True

            else:
                stato_led_verde = False
                stato_led_rosso = False

            dpg.set_value("temperature", f"Temperature: {data[1]} °C")
            dpg.set_value("humidity", f"Humidity: {data[0]} %")
            dpg.set_value("leds", f"Led Verde: {stato_led_verde} | Led Rosso: {stato_led_rosso}")

            dpg.set_value("temperatureData", [intervals, temperature])
            dpg.set_value("humidityData", [intervals, humidity])

        dpg.render_dearpygui_frame()

    dpg.destroy_context()
