from machine import Pin, SPI, I2C, PWM
import max7219
import sh1106
import time
import network
import socket
import dht

led = Pin("LED", Pin.OUT)

ssid = "nimic"
password = "mateiurea314"


def connect_wifi():
    display.fill(0)
    display.text("se conecteaza", 0, 0, 1)
    display.text("la wifi...", 0, 10, 1)
    display.show()

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for connect or fail
    max_wait = 100

    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1

        led.toggle()
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError("network connection failed")
    else:
        status = wlan.ifconfig()

        display.fill(0)
        display.text("ip = ", 0, 0, 1)
        display.text(status[0], 0, 10, 1)
        display.show()
        led.on()

        return status[0]


# partea de lcd
i2c = I2C(1, sda=Pin(26), scl=Pin(27), freq=400000)
devices = i2c.scan()
display = sh1106.SH1106_I2C(128, 64, i2c, None, 0x3C)
display.fill(0)
display.sleep(False)

#partea de temp.
sensor = dht.DHT22(Pin(0))
temp = 0
hum = 0

# PINI MATRICE
CLK = 18  # SPI0
DIN = 19  # SPI0 MOSI (TX)
CS = 13  # Any GPIO pin

# microfon
sound = Pin(15, Pin.IN)
# ledul RGB
led_B = PWM(Pin(3))
led_B.freq(1000)

led_G = PWM(Pin(2))
led_G.freq(1000)

led_R = PWM(Pin(4))
led_R.freq(1000)

def R_on():
    led_R.duty_u16(1500)

def R_off():
    led_R.duty_u16(0)
    
def G_on():
    led_G.duty_u16(1500)


def G_off():
    led_G.duty_u16(0)


def B_on():
    led_B.duty_u16(1500)


def B_off():
    led_B.duty_u16(0)
# Initialize SPI
spi = SPI(0, baudrate=10000000, polarity=0, phase=0, sck=Pin(CLK), mosi=Pin(DIN))

# Initialize MAX7219 matrix
matrix = max7219.Matrix8x8(spi, Pin(CS), 1)


def test_all_leds():
    display.text("testare leduri...", 0, 0, 1)
    display.show()

    matrix.fill(0)
    matrix.show()
    time.sleep(1)

    for x in range(8):
        for y in range(8):
            matrix.pixel(x, y, 1)
            matrix.show()
            time.sleep(0.01)

    for x in range(8):
        for y in range(8):
            matrix.pixel(x, y, 0)
            matrix.show()
            time.sleep(0.01)

        # background-image: url("/background-image.jpg");


def get_html(ip):
    return """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Proiect SI</title>
    <style>
      body {{
        font-family: Arial, sans-serif;
        text-align: center;
        margin: 20px;
      }}
      #content {{
        margin-top: 20px;
        padding: 20px;
        border: 1px solid #ccc;
        border-radius: 5px;
        background-color: #f9f9f9;
      }}
      button {{
        margin: 5px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        border: 1px solid #ccc;
        border-radius: 5px;
        background-color: #007bff;
        color: white;
      }}
      button:hover {{
        background-color: #0056b3;
      }}
      table {{
        border-collapse: collapse;
        margin: 20px auto;
      }}
      td {{
        padding: 10px;
        text-align: center;
      }}
      input[type="checkbox"] {{
        appearance: none;
        -webkit-appearance: none;
        width: 20px;
        height: 20px;
        border: 2px solid #ccc;
        border-radius: 50%;
        outline: none;
        cursor: pointer;
      }}
      input[type="checkbox"]:checked {{
        background-color: #007bff;
        border-color: #007bff;
      }}
    </style>
  </head>
  <body>
    <h1>Proiect SI</h1>
    <button onclick="showWeather()">Weather</button>
    <button onclick="showAnimation()">Animation</button>
    <div id="content">
      <p>Click a button to see content!</p>
    </div>

    <script>
      const html = String.raw;

      let animationDelay = 500;

      const matrice = Array.from({{ length: 8 }}, () =>
        Array.from({{ length: 8 }}, () => false)
      );
      const frames = [];
      let animationStarted = false;

      function showWeather() {{
        fetch('/weather')
          .then(response => response.json())
          .then(data => {{
            document.getElementById("content").innerHTML = `
              <h2>Weather Update</h2>
              <p>Temperature: ${{data.temperature}}°C</p>
              <p>Humidity: ${{data.humidity}}%</p>
            `;
          }})
          .catch(error => {{
            document.getElementById("content").innerHTML = `
              <h2>Error</h2>
              <p>Unable to fetch weather data. Please try again later.</p>
            `;
            console.error("Error fetching weather data:", error);
          }});
      }}


      function setSpeed(delay) {{
        stopAnimation();

        animationDelay = delay;

        startAnimation();
      }}

      function toggleLed(i, j) {{
        matrice[i][j] = !matrice[i][j];
        console.log(matrice);
      }}

      function addFrame() {{
        if (frames.length < 8) {{
          // Clone the current matrix and add it as a frame
          frames.push(matrice.map((row) => [...row]));
          console.log("Frame added:", frames);
        }} else {{
          alert("Maximum of 8 frames reached!");
        }}
      }}

      const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

      async function startAnimation() {{
        if (frames.length === 0) {{
          alert("No frames to display! Add some frames first.");
          return;
        }}

        let currentFrame = 0;

        animationStarted = true;

        while (animationStarted) {{
          const frame = frames[currentFrame];

          // de forma 1,1;2,2;3,4; etc
          let updates = "";

          for (let i = 0; i < frame.length; i++) {{
            for (let j = 0; j < frame[i].length; j++) {{
              const checkbox = document.getElementById(`button-${{i}}-${{j}}`);

              checkbox.checked = frame[i][j];

              if (checkbox.checked) {{
                updates += `${{i}},${{j}};`;
              }}
            }}
          }}

          currentFrame = (currentFrame + 1) % frames.length;

          await Promise.allSettled([
            sleep(animationDelay),
            fetch(`http://{ip}/led/${{updates}}`),
          ]);
        }}
      }}

      function stopAnimation() {{
        animationStarted = false;
      }}

      function showAnimation() {{
        let content = html``;

        for (let i = 7; i >= 0; i--) {{
          content += `<tr>`;
          for (let j = 0; j < 8; j++) {{
            content += html`<td>
              <input
                type="checkbox"
                onclick="toggleLed(${{i}}, ${{j}})"
                name="button-${{i}}-${{j}}"
                id="button-${{i}}-${{j}}"
              />
            </td>`;
          }}
          content += `</tr>`;
        }}

        // Add the "Add", "Start", and "Stop" buttons
        content += html`
          <tr>
            <td colspan="8">
              <button onclick="addFrame()">Add</button>
              <button onclick="startAnimation()">Start</button>
              <button onclick="stopAnimation()">Stop</button>
            </td>
          </tr>
          <tr>
            <td colspan="8">
              <button onclick="setSpeed(2000)">Very Slow</button>
              <button onclick="setSpeed(1000)">Slow</button>
              <button onclick="setSpeed(500)">Normal</button>
              <button onclick="setSpeed(250)">Fast</button>
              <button onclick="setSpeed(125)">Very Fast</button>
            </td>
          </tr>
        `;

        document.getElementById("content").innerHTML = html`<table>
          <tbody>
            ${{content}}
          </tbody>
        </table>`;
      }}
    </script>
  </body>
</html>
""".format(
        ip=ip
    )


def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection


def serve(connection, ip):

    while True:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        if sound.value() == 1:
            G_on()
            R_off()
        else:
            G_off()
            R_on()

        client = connection.accept()[0]
        request = client.recv(1024).decode("utf-8")
        request_path = request.split(" ")[1]

        if request_path == "/":
            client.send("HTTP/1.1 200 OK\n")
            client.send("Content-Type: text/html\n")
            client.send("Connection: close\n\n")
            client.sendall(get_html(ip))

        elif request_path.startswith("/led/"):
            coordinates_str = request_path[
                len("/led/") :
            ]  # Extract the part after "/led/"
            coordinates_list = coordinates_str.strip(";").split(
                ";"
            )  # Split by semicolons and remove trailing semicolon

            for x in range(8):
                for y in range(8):
                    matrix.pixel(x, y, False)

            for coordinate in coordinates_list:
                if "," in coordinate:  # Ensure it contains a comma
                    xStr, yStr = coordinate.split(",")
                    x = int(xStr)
                    y = int(yStr)

                    # Validate and toggle the pixel
                    if 0 <= x < 8 and 0 <= y < 8:
                        matrix.pixel(x, y, True)

            matrix.show()

            client.send("HTTP/1.1 200 OK\n")
            client.send("Connection: close\n\n")

        elif request_path == "/weather":
            # Prepare the JSON response
            response = '{{"temperature": {:.2f}, "humidity": {:.2f}}}'.format(temp, hum)
            if(temp > 20):
              R_on()
              B_off()
            else:
              B_on()
              R_off()
            # Send HTTP headers
            client.send("HTTP/1.1 200 OK\n")
            client.send("Content-Type: application/json\n")
            client.send("Connection: close\n\n")
            client.sendall(response)

        client.close()


if __name__ == "__main__":
    led.off()
    test_all_leds()

    ip = connect_wifi()
    conn = open_socket(ip)
    serve(conn, ip)
 