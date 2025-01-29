import serial

# crea la seriale
ser = serial.Serial("COM4", 9600)

while True:
    print("sto leggendo...")
    # legge i dati (o meglio, legge i byte di dati)
    data = ser.readline()
    print("codifica in corso...")
    # li converte in una stringa utf-8
    data = data.decode("utf-8")
    print("codificato")
    #mette in due variabili, T e H come arduino
    h, t = data.split(' ')

    #converte in interi
    h = int(h)
    t = int(t)

    #stampa a video
    print(f"Temperatura = {t}, umidita' = {h}")

ser.close()  # chiudi la seriale
