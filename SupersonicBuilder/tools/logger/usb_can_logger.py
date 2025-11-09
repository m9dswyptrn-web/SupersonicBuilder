#!/usr/bin/env python3

# USB CAN Logger for SonicBuilder (JSON lines -> CSV), v2.2.0
# - Reads JSON frames from Teensy41 over USB CDC
# - Writes CSV (bus,id,dlc,data,ts) and rolling log
# - Python deps: pyserial
# - Termux/Android example: termux-usb -r /dev/bus/usb/001/002 then use the tty created.
import sys, json, csv, time, argparse
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True, help="Serial port (e.g., /dev/ttyACM0, COM5)")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--out", default="can_log.csv")
    A = ap.parse_args()

    try:
        import serial
    except ImportError:
        print("Install pyserial: pip install pyserial"); sys.exit(2)

    ser = serial.Serial(A.port, A.baud, timeout=0.25)
    outp = Path(A.out)
    f = outp.open("a", newline="")
    w = csv.writer(f)
    if outp.stat().st_size == 0:
        w.writerow(["t_wall","bus","id","dlc","data","ts"])

    buf = b""
    try:
        while True:
            chunk = ser.read(1024)
            if chunk:
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    s = line.decode("utf-8", errors="ignore").strip()
                    if not s or s.startswith("#"):
                        continue
                    try:
                        obj = json.loads(s)
                        w.writerow([time.time(), obj.get("bus",""), obj.get("id",""),
                                    obj.get("dlc",""), obj.get("data",""), obj.get("ts","")])
                    except Exception:
                        # Not JSON, ignore
                        pass
            else:
                time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        f.close()
        ser.close()

if __name__ == "__main__":
    main()
