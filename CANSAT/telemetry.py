from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
import threading
import time


class XBeeReceiver:
    """
    Opens a serial connection to an XBee module,
    sends a 'start' command via unicast to a target address,
    and collects incoming packets into data_packets[].
    """

    def __init__(self, port: str, baud_rate: int = 9600):
        self.port = port
        self.baud_rate = baud_rate
        self.device = XBeeDevice(self.port, self.baud_rate)
        self.data_packets = []
        self._stop_event = threading.Event()
        self._thread = None

        # --- target 64-bit address for unicast ---
        self.remote_address_str = "0013A20041068422"
        self.remote_device = None

    def start(self):
        """Open XBee, send start command, and begin background listener."""
        self.device.open()
        print(f"[XBeeReceiver] Opened {self.port} @ {self.baud_rate}")

        # Build remote device object once
        try:
            self.remote_device = RemoteXBeeDevice(
                self.device, XBee64BitAddress.from_hex_string(self.remote_address_str)
            )
            print(f"[XBeeReceiver] Remote device set to {self.remote_address_str}")
        except Exception as e:
            print(f"[XBeeReceiver] Error setting remote address: {e}")

        # Send the start command via unicast
        self.send_start_command()

        # Start listening
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()

    def send_start_command(self):
        """Send 'start' command to the remote XBee (unicast)."""
        try:
            if self.device.is_open() and self.remote_device:
                msg = " start"
                self.device.send_data(self.remote_device, msg)
                print(f"[XBeeReceiver] Sent unicast start → {self.remote_address_str}")
                time.sleep(0.2)
            else:
                print("[XBeeReceiver] Cannot send start — device or remote not ready.")
        except Exception as e:
            print(f"[XBeeReceiver] Failed to send start command: {e}")

    def _receive_loop(self):
        """Continuously read incoming packets."""
        while not self._stop_event.is_set():
            try:
                xbee_msg = self.device.read_data(timeout=5)
                if xbee_msg and xbee_msg.data:
                    self.data_packets.append(xbee_msg.data)
            except Exception as e:
                print(f"[XBeeReceiver] read error: {e}")

    def stop(self):
        """Stop background thread and close device."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.5)
        if self.device.is_open():
            try:
                self.device.close()
                print(f"[XBeeReceiver] Closed {self.port}")
            except Exception:
                pass
