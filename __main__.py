import mset
import rtmidi
import sys
import threading
import queue
import time


MIDI_NAME = "ATOM"
midi_controller = None
poll_thread = None
kju = queue.Queue()
kill_kju = queue.Queue()


def set_callbacks():
    mset.callbacks.onPeriodicUpdate = read_q
    mset.callbacks.onRegainFocus = None
    mset.callbacks.onSceneChanged = None
    mset.callbacks.onSceneLoaded = None
    mset.callbacks.onShutdownPlugin = None


def clear_callbacks():
    mset.callbacks.onPeriodicUpdate = None
    mset.callbacks.onRegainFocus = None
    mset.callbacks.onSceneChanged = None
    mset.callbacks.onSceneLoaded = None
    mset.callbacks.onShutdownPlugin = None


def start_polling():
    set_callbacks()
    poll_thread = threading.Thread(target=poll, args=(midi_controller, kju, kill_kju))
    poll_thread.start()


def stop_polling():
    clear_callbacks()
    kill_kju.put("STOP")
    poll_thread.join()
    poll_thread = None


def bye():
    stop_polling()
    print("bye")
    # I can't open the plugin more than once because Python complains that the
    # rtmidi module can't be imported more than once. Manually unimporting it
    # then.
    sys.modules.pop('rtmidi')
    mset.shutdownPlugin()


def read_q():
    print("reading q...")
    m = kju.get_nowait()
    print(m)
    kju.task_done()


def poll(midi_controller, kju_out, kju_in):
    while True:
        time.sleep(0.15)
        c = kju_in.get_nowait()
        kju_in.task_done()
        if c == "STOP":
            return

        if midi_controller != None and midi_controller.is_port_open():
            #print("Polling...")
            m = midi_controller.get_message()

            if m:
                kju_out.put(m)
        else:
            pass
            #print("Can't poll because midi_controller is dead...")

    print("Midi thread exiting...")


def open_device():
    midi_in = rtmidi.MidiIn()
    ports = range(midi_in.get_port_count())
    midi_controller = None
    if ports:
        for p in ports:
            port_name = midi_in.get_port_name(p)
            print(port_name)
            if MIDI_NAME in port_name:
                print(f"Opening port {p}:{port_name}")
                midi_controller = midi_in.open_port(p)
    return (f"Detected midi: {len(ports)}", midi_controller)


window = mset.UIWindow("MidiControl")

button = mset.UIButton("Start polling")
button.onClick = start_polling
window.addElement(button)
window.addReturn()
button = mset.UIButton("Stop polling")
button.onClick = stop_polling
window.addElement(button)
window.addReturn()
button = mset.UIButton("Shutdown")
button.onClick = bye
window.addElement(button)
window.addReturn()

midi_status = mset.UILabel()
window.addElement(midi_status)

midi_status.text, midi_controller = open_device()


BUTTON_TO_BUTTON_ID = {
    "A1_1": 36, "A1_2": 52,
    "A2_1": 37, "A2_2": 53,
    "A3_1": 38, "A3_2": 54,
    "A4_1": 39, "A4_2": 55,
    "B1_1": 40, "B1_2": 56,
    "B2_1": 41, "B2_2": 57,
    "B3_1": 42, "B3_2": 58,
    "B4_1": 43, "B4_2": 59,
    "C1_1": 44, "C1_2": 60,
    "C2_1": 45, "C2_2": 61,
    "C3_1": 46, "C3_2": 62,
    "C4_1": 47, "C4_2": 63,
    "D1_1": 48, "D1_2": 64,
    "D2_1": 49, "D2_2": 65,
    "D3_1": 50, "D3_2": 66,
    "D4_1": 51, "D4_2": 67
}

