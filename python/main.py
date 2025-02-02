from queue import Empty

import serial
import dearpygui.dearpygui as dpg
import multiprocessing as mp


def read_data(q):
    # crea la seriale
    porta_seriale = "COM3"
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

    # dichiarazione lista dei dati
    data = [0, 0]
    temperature = [0 for i in range(60)]
    humidity = [0 for i in range(60)]
    intervals = [i for i in range(60)]

    # creazione gui
    dpg.create_context()
    dpg.create_viewport(title='Data Reader')

    # aggiunta delle caselle di testo contenenti le varie informazioni
    with dpg.window(label="Data Reader"):
        # aggiunta dati
        dpg.add_text("", tag="data")

        with dpg.plot(label="Temperature Variation", height=400, width=800, tag="temperaturePlot"):
            # dichiarazione assi
            dpg.add_plot_axis(dpg.mvXAxis, label="time (s)", tag="timeAxis1")
            dpg.add_plot_axis(dpg.mvYAxis, label="temperature (C)", tag="temperatureAxis")

            # impostazione limiti degli assi
            dpg.set_axis_limits("timeAxis1", 0, 60)
            dpg.set_axis_limits("temperatureAxis", -20, 50)

            # aggiunta delle linee
            dpg.add_line_series(temperature, intervals, parent="temperatureAxis", tag="temperatureData",
                                label="Temperature")

        with dpg.plot(label="Humidity Variation", height=400, width=800, tag="humidityPlot"):
            # dichiarazione assi
            dpg.add_plot_axis(dpg.mvXAxis, label="time (s)", tag="timeAxis2")
            dpg.add_plot_axis(dpg.mvYAxis, label="humidity (%)", tag="humidityAxis")

            # impostazione limiti degli assi
            dpg.set_axis_limits("timeAxis2", 0, 60)
            dpg.set_axis_limits("humidityAxis", 0, 100)

            # aggiunta delle linee
            dpg.add_line_series(temperature, intervals, parent="humidityAxis", tag="humidityData",
                                label="Humidity")

    # inizializzazione gui
    dpg.setup_dearpygui()
    dpg.show_viewport()

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

            dpg.set_value("data", data)
            dpg.set_value('temperatureData', [intervals, temperature])
            dpg.set_value("humidityData", [intervals, humidity])

        dpg.render_dearpygui_frame()


    dpg.destroy_context()
