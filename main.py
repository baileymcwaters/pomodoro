import os
import time
import curses
from curses import wrapper
from plyer import notification

def send_notification(title: str, message: str) -> None:
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Pomodoro',
            timeout=5
        )
    except Exception:
        # If notifications fail (e.g., environment not supported), ignore
        pass

def get_time():
    return time.monotonic()

def s_to_tc(seconds: int) -> str:
    h = str(seconds // 3600).zfill(2)
    m = str((seconds % 3600) // 60).zfill(2)
    s = str(seconds % 60).zfill(2)
    return f"{h}:{m}:{s}"

def main(stdscr) -> None:
    ss_dur = 1500
    sb_dur = 300
    lb_dur = 900
    sb_completed = 0
    is_paused = False
    is_study = True
    is_sb = False
    curses.curs_set(0)
    stdscr.timeout(200)
    clock = ss_dur
    last_tick = get_time()
    send_notification(
        title='Pomodoro started',
        message=f'Focused session for {ss_dur // 60} minutes'
    )
    while True:
        if is_study:
            session = "Pomodoro"
        elif is_sb:
            session = "Short Break"
        else:
            session = "Long Break"
        timer = s_to_tc(clock)
        status = "PAUSED" if is_paused else ""

        height, width = stdscr.getmaxyx()
        x = width // 2 - len(timer) // 2
        y = height // 2

        stdscr.clear()
        stdscr.addstr(y, x, timer)
        stdscr.addstr(height-1,(width // 2 - len(status) // 2),status)
        stdscr.addstr(0,(width // 2 - len(session) // 2),session)
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord('p'):
            is_paused = not is_paused
            last_tick = get_time()

        if key == curses.KEY_RESIZE:
            pass
        now = get_time()
        if is_paused:
            last_tick = now
        else:
            elapsed = now - last_tick
            if elapsed >= 1:
                dec = int(elapsed)
                last_tick += dec

                remaining = dec
                while remaining > 0:
                    if remaining < clock:
                        clock -= remaining
                        remaining = 0
                    else:
                        remaining -= clock
                        if is_sb:
                            is_study = True
                            is_sb = False
                            sb_completed = sb_completed + 1
                            clock = ss_dur
                            send_notification(
                                title='Pomodoro started',
                                message=f'Focused session for {ss_dur // 60} minutes'
                            )
                        elif not is_study and not is_sb:
                            is_study = True
                            clock = ss_dur
                            sb_completed = 0
                            send_notification(
                                title='Pomodoro started',
                                message=f'Focused session for {ss_dur // 60} minutes'
                            )
                        elif is_study and sb_completed == 3:
                            is_study = False
                            is_sb = False
                            clock = lb_dur
                            send_notification(
                                title='Long break started',
                                message=f'Long break for {lb_dur // 60} minutes'
                            )
                        else:
                            is_study = False
                            is_sb = True
                            clock = sb_dur
                            send_notification(
                                title='Short break started',
                                message=f'Short break for {sb_dur // 60} minutes'
                            )

if __name__ == '__main__':
    wrapper(main)
