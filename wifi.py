from machine import Pin
from utime import sleep
import network
import socket

#wifi
SSID = "ALHN-2061"
PASSWORD = "92E5XNmQQP"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("Conectando a la red...")
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    sleep(1)

print('Conexión establecida')
ip = wlan.ifconfig()[0]
print('Dirección IP:', ip)


led = Pin(2, Pin.OUT)  

# Configuración del servidor web

addr = socket.getaddrinfo(ip, 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print("Servidor web corriendo en", ip)

while True:
    cl, addr = s.accept()
    print('Cliente conectado desde', addr)
    request = cl.recv(1024).decode('utf-8')
    print("Solicitud recibida:", request)
    
    # Manejo de rutas
    if 'GET /led/on' in request:
        led.value(1)
        print("LED encendido")
    elif 'GET /led/off' in request:
        led.value(0)
        print("LED apagado")
    
   
    response = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n
<html>
<head>
    <title>ESP32 LED Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #282c36;
            color: white;
            margin: 0;
            padding: 20px;
        }
        h1 {
            margin-bottom: 20px;
        }
        .button {
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
        }
        .on {
            background-color: #28a745;
        }
        .on:hover {
            background-color: #218838;
        }
        .off {
            background-color: #dc3545;
        }
        .off:hover {
            background-color: #c82333;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Control del LED</h1>
        <a href="/led/on" class="button on">Encender</a>
        <a href="/led/off" class="button off">Apagar</a>
    </div>
</body>
</html>
"""

    
    cl.send(response)
    cl.close()
