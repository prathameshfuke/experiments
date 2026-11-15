"""EXP 06 - Turn a lamp on/off from a browser on the LAN (Raspberry Pi)
WIRING
  GPIO17 (pin 11) -> 330R -> LED(+) ; LED(-) -> pin 6 (GND)
STEPS
  1. pip3 install flask gpiozero
  2. Wire as above. Pi and your phone/PC on the same Wi-Fi.
  3. Run:  python3 lan_bulb.py   (find the Pi address with:  hostname -I)
  4. Browser: http://<pi-ip>:5000  Press ON / OFF: the LED and the page status change.
"""
from flask import Flask, request, redirect
from gpiozero import LED

app = Flask(__name__)
lamp = LED(17)

@app.get("/")
def home():
    state = "ON" if lamp.is_lit else "OFF"
    return (f"<h2>Lamp status: {state}</h2>"
            "<form method=post action=/set>"
            "<button name=state value=on>ON</button>"
            "<button name=state value=off>OFF</button></form>")

@app.post("/set")
def set_lamp():
    if request.form.get("state") == "on":
        lamp.on()
    else:
        lamp.off()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
