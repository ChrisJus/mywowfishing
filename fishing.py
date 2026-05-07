# _*_coding:utf-8_*_
# Author      :ories
# File_Name   :fishing.py
# Create_Date :2026-05-07
# Description :wow fishing script
# IDE         :PyCharm
import random
import threading
import time
import tkinter as tk
from collections import deque

import numpy as np
import Quartz
from AppKit import NSWorkspace
from catap import (
    AudioBuffer,
    AudioProcess,
    AmbiguousAudioProcessError,
    find_process_by_name,
    list_audio_processes,
    record_process,
    record_system_audio,
)

# 改成 True 为测试
DEV = False
TIMEOUT = 120
START_DELAY = 2
KEY_TO_PRESS = '0'
THRESHOLD_DEFAULT = 0.089
RECENT_PEAK_WINDOW = 12
TARGET_APP_HINTS = ['Wow', 'World of Warcraft', 'Warcraft', '魔兽世界']
TARGET_AUDIO_HINTS = ['Wow', 'World of Warcraft', 'Warcraft', 'Battle.net', 'wxplayer', '魔兽世界']
KEY_CODE_MAP = {
    '0': 29,
}


def find_target_pid() -> int:
    apps = NSWorkspace.sharedWorkspace().runningApplications()
    for app in apps:
        name = app.localizedName() or ''
        for hint in TARGET_APP_HINTS:
            if hint.lower() in name.lower():
                pid = int(app.processIdentifier())
                print(f'Using target app: {name} (pid: {pid})')
                return pid

    running_names = sorted(
        {
            (app.localizedName() or '').strip()
            for app in apps
            if (app.localizedName() or '').strip()
        }
    )
    raise RuntimeError(
        'Target app not found.\n'
        f'Expected one of: {", ".join(TARGET_APP_HINTS)}\n'
        'Running applications:\n' + '\n'.join(running_names)
    )


def _find_target_audio_process() -> AudioProcess:
    for hint in TARGET_AUDIO_HINTS:
        try:
            process = find_process_by_name(hint)
        except AmbiguousAudioProcessError as exc:
            print(f'Audio process match is ambiguous for {hint}: {exc}')
            continue

        if process is not None:
            print(
                'Using target audio process: '
                f'{process.name} (pid: {process.pid}, '
                f'audio_id: {process.audio_object_id}, '
                f'bundle: {process.bundle_id or "N/A"})'
            )
            return process

    running_processes = list_audio_processes()
    formatted = [
        f'{process.name} (PID: {process.pid}, Audio ID: {process.audio_object_id}, '
        f'Bundle: {process.bundle_id or "N/A"}, outputting={process.is_outputting})'
        for process in running_processes
    ]
    raise RuntimeError(
        'Target audio process not found.\n'
        f'Expected one of: {", ".join(TARGET_AUDIO_HINTS)}\n'
        'Available audio processes:\n' + '\n'.join(formatted)
    )


def _build_recording_session(on_buffer):
    try:
        process = _find_target_audio_process()
        return record_process(process, on_buffer=on_buffer), f'audio process {process.name}'
    except Exception as exc:
        print(f'{exc}\nFalling back to system audio capture.')
        return record_system_audio(on_buffer=on_buffer), 'system audio'


def press_key_to_pid(pid, key=KEY_TO_PRESS):
    keycode = KEY_CODE_MAP.get(key)
    if keycode is None:
        raise ValueError(f'Unsupported key: {key}')

    print(f'Pressing key: {key} -> pid {pid}')
    source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)
    key_down = Quartz.CGEventCreateKeyboardEvent(source, keycode, True)
    key_up = Quartz.CGEventCreateKeyboardEvent(source, keycode, False)
    Quartz.CGEventPostToPid(int(pid), key_down)
    Quartz.CGEventPostToPid(int(pid), key_up)


def _buffer_samples(buffer: AudioBuffer) -> np.ndarray:
    fmt = buffer.format
    if fmt.is_float:
        if fmt.bits_per_sample == 32:
            dtype = np.float32
        elif fmt.bits_per_sample == 64:
            dtype = np.float64
        else:
            raise ValueError(f'Unsupported float format: {fmt.bits_per_sample}-bit')
        return np.frombuffer(buffer.data, dtype=dtype).astype(np.float64, copy=False)

    if not fmt.is_signed_integer:
        raise ValueError(
            f'Unsupported sample type: {fmt.sample_type} ({fmt.bits_per_sample}-bit)'
        )

    if fmt.bits_per_sample == 8:
        dtype = np.int8
    elif fmt.bits_per_sample == 16:
        dtype = np.int16
    elif fmt.bits_per_sample == 32:
        dtype = np.int32
    else:
        raise ValueError(f'Unsupported integer format: {fmt.bits_per_sample}-bit')

    samples = np.frombuffer(buffer.data, dtype=dtype).astype(np.float64)
    max_abs = float(1 << (fmt.bits_per_sample - 1))
    return samples / max_abs


def _buffer_volume(buffer: AudioBuffer) -> float:
    samples = _buffer_samples(buffer)
    if samples.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(samples))))


def listen(stop_event, timeout=TIMEOUT, threshold=THRESHOLD_DEFAULT):
    print(
        'Well, now we are listening for game internal sounds, '
        f'timeout: {timeout} seconds, threshold: {threshold}...'
    )
    history = deque(maxlen=RECENT_PEAK_WINDOW)
    triggered = threading.Event()
    start_time = time.time()

    def on_buffer(buffer: AudioBuffer):
        if stop_event.is_set() or triggered.is_set():
            return

        volume = _buffer_volume(buffer)
        print(f'[{source_label}] Volume: {volume:.4f}')
        history.append(volume)
        recent_peak = max(history)
        print(f'[{source_label}] Recent peak({len(history)}): {recent_peak:.4f}')
        if recent_peak > threshold:
            print('I heard something!')
            triggered.set()

    session, source_label = _build_recording_session(on_buffer)

    try:
        with session:
            while (
                time.time() - start_time < timeout
                and not triggered.is_set()
                and not stop_event.is_set()
            ):
                time.sleep(0.05)
    except Exception as exc:
        print(f'Audio device error: {exc}')
        return False

    if stop_event.is_set():
        print('Stopped listening.')
        return None

    if not triggered.is_set():
        print(f'I do not hear anything already {timeout} seconds!')
    return triggered.is_set()


class FishingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('钓鱼')
        self.root.geometry('260x120')
        self.root.resizable(False, False)

        self.stop_event = threading.Event()
        self.worker = None
        self.status_var = tk.StringVar(value='未启动')
        self.threshold_var = tk.DoubleVar(value=THRESHOLD_DEFAULT)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        self.start_button = tk.Button(button_frame, text='启动', width=10, command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(button_frame, text='停止', width=10, command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        tk.Label(self.root, textvariable=self.status_var).pack(pady=5)
        threshold_frame = tk.Frame(self.root)
        threshold_frame.pack(pady=2)
        tk.Label(threshold_frame, text='阈值(0~1)').pack(side=tk.LEFT)
        tk.Entry(threshold_frame, textvariable=self.threshold_var, width=8).pack(side=tk.LEFT, padx=6)
        self.root.protocol('WM_DELETE_WINDOW', self.close)

    def set_status(self, text):
        print(text)
        try:
            self.root.after(0, lambda: self.status_var.set(text))
        except tk.TclError:
            pass

    def set_running_ui(self, running):
        def update():
            self.start_button.config(state=tk.DISABLED if running else tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL if running else tk.DISABLED)

        try:
            self.root.after(0, update)
        except tk.TclError:
            pass

    def sleep_interruptible(self, seconds):
        end_time = time.time() + seconds
        while time.time() < end_time:
            if self.stop_event.is_set():
                return True
            time.sleep(min(0.1, end_time - time.time()))
        return self.stop_event.is_set()

    def start(self):
        if self.worker and self.worker.is_alive():
            return

        self.stop_event.clear()
        self.set_running_ui(True)
        self.worker = threading.Thread(target=self.run_script, daemon=True)
        self.worker.start()

    def stop(self):
        self.set_status('正在停止...')
        self.stop_event.set()

    def run_script(self):
        try:
            target_pid = find_target_pid()
            self.set_status(f'目标进程 PID: {target_pid}')
            self.set_status(f'启动后等待 {START_DELAY} 秒...')
            if self.sleep_interruptible(START_DELAY):
                return

            press_key_to_pid(target_pid)

            while not self.stop_event.is_set():
                threshold = float(self.threshold_var.get())
                self.set_status(f'监听中，最长 {TIMEOUT} 秒，阈值 {threshold:.4f}...')
                result = listen(self.stop_event, threshold=threshold)

                if result is None or self.stop_event.is_set():
                    break

                if result:
                    self.set_status('检测到声音，按 0')
                    press_key_to_pid(target_pid)
                    sleep_time = random.uniform(1, 3)
                    self.set_status(f'等待 {sleep_time:.2f} 秒后再次按 0')
                    if self.sleep_interruptible(sleep_time):
                        break
                    press_key_to_pid(target_pid)
                else:
                    self.set_status(f'{TIMEOUT} 秒未检测到声音，重复按 0')
                    press_key_to_pid(target_pid)
        except Exception as exc:
            self.set_status(f'错误：{exc}')
        finally:
            self.stop_event.set()
            self.set_running_ui(False)
            if self.status_var.get() == '正在停止...':
                self.set_status('已停止')

    def close(self):
        self.stop_event.set()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    FishingApp().run()
