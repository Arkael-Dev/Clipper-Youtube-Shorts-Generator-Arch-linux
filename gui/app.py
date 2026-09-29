#!/usr/bin/python3

import os
import subprocess
import threading
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Pango


ROOT = Path(__file__).resolve().parent.parent
RUN_SCRIPT = ROOT / "run.sh"
OUTPUT_DIR = Path.home() / "CLIPPER"


class ShortsGUI(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.arkael.aiyoutubeshortsgenerator"
        )

    def do_activate(self):
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title("AI YouTube Shorts Generator")
        self.window.set_default_size(900, 700)

        self.build_ui()
        self.window.present()

    def build_ui(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.window.set_child(root)

        header = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4
        )
        header.set_margin_top(24)
        header.set_margin_bottom(18)
        header.set_margin_start(28)
        header.set_margin_end(28)

        title = Gtk.Label(label="AI YOUTUBE SHORTS GENERATOR")
        title.set_xalign(0)
        title.add_css_class("title")

        subtitle = Gtk.Label(
            label="Local AI • Ollama • Whisper • FFmpeg"
        )
        subtitle.set_xalign(0)
        subtitle.add_css_class("subtitle")

        developer = Gtk.Label(label="Developer: Arkael-Dev")
        developer.set_xalign(0)
        developer.add_css_class("developer")

        header.append(title)
        header.append(subtitle)
        header.append(developer)

        root.append(header)

        separator = Gtk.Separator()
        root.append(separator)

        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(28)
        content.set_margin_end(28)

        url_label = Gtk.Label(label="YouTube URL")
        url_label.set_xalign(0)
        url_label.add_css_class("section")

        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text(
            "https://www.youtube.com/watch?v=..."
        )
        self.url_entry.set_hexpand(True)

        content.append(url_label)
        content.append(self.url_entry)

        options = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=20
        )

        resolution_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )
        resolution_box.set_hexpand(True)

        resolution_label = Gtk.Label(label="Output Resolution")
        resolution_label.set_xalign(0)
        resolution_label.add_css_class("section")

        self.resolution = Gtk.DropDown.new_from_strings([
            "720 × 1280",
            "1080 × 1920",
        ])

        resolution_box.append(resolution_label)
        resolution_box.append(self.resolution)

        color_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )
        color_box.set_hexpand(True)

        color_label = Gtk.Label(label="Subtitle Color")
        color_label.set_xalign(0)
        color_label.add_css_class("section")

        self.color = Gtk.DropDown.new_from_strings([
            "White",
            "Yellow",
            "Cyan",
            "Green",
            "Pink",
        ])

        color_box.append(color_label)
        color_box.append(self.color)

        options.append(resolution_box)
        options.append(color_box)

        content.append(options)

        self.custom_color = Gtk.Entry()
        self.custom_color.set_placeholder_text(
            "Custom HEX, example: FF8800"
        )
        self.custom_color.set_visible(False)

        content.append(self.custom_color)

        self.color.connect(
            "notify::selected-item",
            self.on_color_changed
        )

        self.generate_button = Gtk.Button(
            label="Generate Shorts"
        )
        self.generate_button.add_css_class("suggested-action")
        self.generate_button.set_size_request(-1, 48)
        self.generate_button.connect(
            "clicked",
            self.start_generation
        )

        content.append(self.generate_button)

        self.status = Gtk.Label(label="Ready")
        self.status.set_xalign(0)
        self.status.add_css_class("status")

        content.append(self.status)

        self.spinner = Gtk.Spinner()
        self.spinner.set_halign(Gtk.Align.START)
        content.append(self.spinner)

        log_label = Gtk.Label(label="Generator Output")
        log_label.set_xalign(0)
        log_label.add_css_class("section")

        content.append(log_label)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(250)

        self.log = Gtk.TextView()
        self.log.set_editable(False)
        self.log.set_monospace(True)
        self.log.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)

        scrolled.set_child(self.log)
        content.append(scrolled)

        buttons = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )

        self.open_button = Gtk.Button(
            label="Open CLIPPER"
        )
        self.open_button.connect(
            "clicked",
            self.open_clipper
        )

        self.clear_button = Gtk.Button(
            label="Clear Log"
        )
        self.clear_button.connect(
            "clicked",
            self.clear_log
        )

        buttons.append(self.open_button)
        buttons.append(self.clear_button)

        content.append(buttons)

        root.append(content)

        self.load_css()

    def load_css(self):
        css = Gtk.CssProvider()

        css.load_from_data(b"""
        window {
            background: #111318;
        }

        .title {
            font-size: 26px;
            font-weight: 800;
        }

        .subtitle {
            color: #9ca3af;
            font-size: 14px;
        }

        .developer {
            color: #6b7280;
            font-size: 12px;
        }

        .section {
            font-weight: 700;
            margin-bottom: 3px;
        }

        .status {
            font-weight: 700;
        }

        entry,
        dropdown,
        textview {
            border-radius: 8px;
        }

        button {
            min-height: 40px;
        }
        """)

        Gtk.StyleContext.add_provider_for_display(
            self.window.get_display(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_color_changed(self, dropdown, param):
        selected = dropdown.get_selected()

        self.custom_color.set_visible(selected == 5)

    def append_log(self, text):
        def update():
            buffer = self.log.get_buffer()
            end = buffer.get_end_iter()
            buffer.insert(end, text)

            mark = buffer.create_mark(
                None,
                buffer.get_end_iter(),
                False
            )

            self.log.scroll_to_mark(
                mark,
                0.0,
                True,
                0.0,
                1.0
            )

            return False

        GLib.idle_add(update)

    def set_status(self, text):
        GLib.idle_add(
            self.status.set_text,
            text
        )

    def start_generation(self, button):
        url = self.url_entry.get_text().strip()

        if not url:
            self.set_status("Enter a YouTube URL first.")
            return

        resolution = self.resolution.get_selected()

        if resolution == 0:
            resolution_input = "1"
        else:
            resolution_input = "2"

        color = self.color.get_selected()

        if color == 0:
            color_input = "1"
        elif color == 1:
            color_input = "2"
        elif color == 2:
            color_input = "3"
        elif color == 3:
            color_input = "4"
        elif color == 4:
            color_input = "5"
        else:
            color_input = "6"

        if color == 5:
            custom = self.custom_color.get_text().strip()
            if not custom:
                self.set_status("Enter a custom HEX color.")
                return

            color_input += "\n" + custom

        self.generate_button.set_sensitive(False)
        self.spinner.start()
        self.set_status("Generating Shorts...")

        self.append_log(
            "\n==========================================\n"
            "AI YOUTUBE SHORTS GENERATOR\n"
            "==========================================\n"
        )

        threading.Thread(
            target=self.run_generator,
            args=(
                resolution_input,
                color_input,
                url,
            ),
            daemon=True
        ).start()

    def run_generator(
        self,
        resolution,
        color,
        url,
    ):
        try:
            process = subprocess.Popen(
                [str(RUN_SCRIPT)],
                cwd=ROOT,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            inputs = f"{resolution}\n{color}\n{url}\n"

            try:
                process.stdin.write(inputs)
                process.stdin.flush()
                process.stdin.close()
            except BrokenPipeError:
                pass

            for line in process.stdout:
                self.append_log(line)

            return_code = process.wait()

            if return_code == 0:
                self.set_status(
                    "Completed — video saved to ~/CLIPPER"
                )
            else:
                self.set_status(
                    f"Generator failed — exit code {return_code}"
                )

        except Exception as exc:
            self.append_log(
                f"\nGUI ERROR: {exc}\n"
            )
            self.set_status("Generation failed.")

        finally:
            GLib.idle_add(
                self.generate_button.set_sensitive,
                True
            )
            GLib.idle_add(
                self.spinner.stop
            )

    def open_clipper(self, button):
        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        subprocess.Popen(
            ["xdg-open", str(OUTPUT_DIR)]
        )

    def clear_log(self, button):
        self.log.get_buffer().set_text("")


def main():
    app = ShortsGUI()
    app.run(None)


if __name__ == "__main__":
    main()
