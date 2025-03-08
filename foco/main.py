from machine import Pin, PWM
import time
import network
import socket
import _thread 

estado_inicial = 100



SSID = "ALHN-2061"
PASSWORD = "92E5XNmQQP"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected(): 
    time.sleep(1)

print('Conectado a', wlan.ifconfig()[0])


addr = socket.getaddrinfo(wlan.ifconfig()[0], 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print("Servidor web en", wlan.ifconfig()[0])


echo = Pin(7, Pin.IN)
triger = Pin(8, Pin.OUT)
servo_pin = Pin(9)
servo_pwm = PWM(servo_pin, freq=50)


VALOR_ON = 140
VALOR_OFF = 50
foco_estado = False  

def mover_servo(angulo):
    duty = int((angulo / 180.0) * 75 + 40)
    servo_pwm.duty(duty)

def obtener_distancia():
    triger.off()
    time.sleep_us(2)
    triger.on()
    time.sleep_us(10)
    triger.off()

    while echo.value() == 0:
        pass
    start_time = time.ticks_us()

    while echo.value() == 1:
        pass
    end_time = time.ticks_us()

    time_of_flight = time.ticks_diff(end_time, start_time)
    distancia = (time_of_flight * 0.0343) / 2
    return distancia


mover_servo(estado_inicial)

def sensor_hilo():
    global foco_estado
    while True:
        distancia = obtener_distancia()
        print(f"Distancia: {distancia:.2f} cm")

        if distancia <= 5.0:  
            if foco_estado:
                mover_servo(VALOR_OFF)
                foco_estado = False
                print("Foco apagado por sensor")
            else:
                mover_servo(VALOR_ON)
                foco_estado = True
                print("Foco encendido por sensor")

        time.sleep(0.5)  

_thread.start_new_thread(sensor_hilo, ())


while True:
    cl, addr = s.accept()
    print('Cliente conectado desde', addr)
    request = cl.recv(1024).decode('utf-8')

    if 'GET /Foco/on' in request:
        foco_estado = True
        mover_servo(VALOR_ON)
        print("Foco encendido desde web")

    if 'GET /Foco/off' in request:
        foco_estado = False
        mover_servo(VALOR_OFF)
        print("Foco apagado desde web")

    
    response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n
<html>
<head>
    <title>ESP32 LED Control</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #282c36;
            color: white;
            margin: 0;
            padding: 20px;
        }}
        h1 {{ margin-bottom: 20px; }}
        .button {{
            display: inline-block;
            padding: 15px 30px;
            font-size: 18px;
            font-weight: bold;
            text-decoration: none;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: 0.3s;
            margin: 10px;
        }}
        .on {{ background-color: #28a745; }}
        .on:hover {{ background-color: #218838; }}
        .off {{ background-color: #dc3545; }}
        .off:hover {{ background-color: #c82333; }}
        .container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }}
    </style>
    <script>
        function enviarComando(comando) {{
            var xhr = new XMLHttpRequest();
            xhr.open("GET", comando, true);
            xhr.send();
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>Control del foco</h1>
        <button class="button on" onclick="enviarComando('/Foco/on')">Encender</button>
        <button class="button off" onclick="enviarComando('/Foco/off')">Apagar</button>
        <p>Estado del foco: <strong>{"Encendido" if foco_estado else "Apagado"}</strong></p>
    </div>
</body>
</html>
"""
    cl.send(response.encode())
    cl.close()
