#este código interage diretamente com o sistema operacional do raspberry. Não funciona no windows
import RPi.GPIO as gpio
import bluetooth
import bluetooth._bluetooth as bt
import subprocess


def procura_mac():
    dispositivo = bluetooth.discover_devices(duration=1)
    return dispositivo
    

def aciona_gpio(disp_encontrado, mac_address):
    gpio.setmode(gpio.BCM)
    saida = 22
    gpio.setup(saida, gpio.OUT)
    
    
    for mac_encontrado in disp_encontrado:
        for mac_salvo in mac_address:
            if mac_encontrado == mac_salvo:
                #print(disp_encontrado)
                gpio.output(saida, gpio.HIGH)
                
                
    if disp_encontrado == []:
        print("Nenhum dispositivo encontrado.")
        gpio.output(saida, gpio.LOW)
        gpio.cleanup()
        print("-"*50)


def calcula_distancia(rssi):
    n = 3.2     #n -> expoente do caminho-perda
    a = -55    #a -> valor rssi a 1 metro
    return 10**((a - rssi) / (10*n))
    

def RSSI(disp):
    rssi = 0
    out = subprocess.check_output(["sudo", "btmgmt", "find"])
    out = out.decode("ascii", "ignore")
    out_split = out.split()
    
    for i, j in enumerate(out_split):
        if j == disp:
            try:
                rssi = float(out_split[i+4])
            except:
                continue
    
    return rssi


def display_aviso(dist_disp):
          #a  b  c   e   f   g
    seg = [5, 6, 13, 19, 26, 20]
    dist_max = 9

    for i in seg:
        gpio.setup(i, gpio.OUT)

              #a  b  c  e  f  g 
    letra_a = [1, 1, 1, 1, 1, 1]
    letra_f = [1, 0, 0, 1, 1, 1]

    if dist_disp <= dist_max:
        for i, j in enumerate(letra_a):
            gpio.output(seg[i], j)
    elif dist_disp > dist_max:
        for i, j in enumerate(letra_f):
            gpio.output(seg[i], j)
            


if __name__ == "__main__":
    #esta lista deve conter os endereços MAC
    mac_address = [""]
        
    while True:
        try:
            print("Procurando...")
            disp_encontrado = procura_mac()
            aciona_gpio(disp_encontrado, mac_address)
            
            if disp_encontrado != []:
                #print("Calculando distância...")
                for i in disp_encontrado:
                    for j in mac_address:
                        if j == i:
                            print("Calculando distância de " + i + "\nAguade...")
                            rssi = RSSI(i)
                            d = calcula_distancia(rssi)
                            print("dispositivo: {}\nDistância: {:.2f}m"
                                  .format(i, d))
                            print("RSSI: {}dBm".format(rssi))
                            print("-"*50)
                            display_aviso(d)

        except OSError as e:
            print(e)
            gpio.cleanup()
